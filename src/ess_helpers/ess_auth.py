import asyncio
import json
import os
import uuid
import base64
import hashlib
import logging

import nats
from nats.errors import TimeoutError as NatsTimeout, JetStreamError
from nats.js import AckPolicy
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger(__name__)

from .constants import (
    ESS_STREAM_NAME,
    ESS_FILTER_SUBJECTS,
    ESS_MAX_MESSAGES,
    ESS_ENCRYPTION_KEY,
    ESS_SOURCE_FILTER,
    ESS_NKEY_SEED,
    ESS_NKEY_USER,
    ESS_SERVER,
    ESS_ADMIN_USER,
    ESS_ADMIN_PASSWORD
)


def derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()


def decrypt_data(encrypted_b64: str, password: str) -> str:
    key = derive_key(password)
    data = base64.b64decode(encrypted_b64)
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ciphertext, None)
    return decrypted.decode()


def print_msg(m, encryption_key, source_filter):
    try:
        ts = m.info.timestamp_nanos / 1_000_000
        print(
            f"msg seq: {m.seq}, subject: {m.subject}, timestamp: {ts}, "
            f"streamSequence: {m.info.stream_sequence}, deliverySequence: {m.info.delivery_sequence}"
        )
        data = json.loads(m.data.decode())
        process = True
        if source_filter:
            process = data.get("meta", {}).get("source") == source_filter
            if not process:
                src = data.get("meta", {}).get("source")
                print(f" not processing message. filter = {source_filter}, meta.source = {src}")
        if process:
            print(data)
            try:
                if data.get("error"):
                    print(f"error with payload: {data['error']['message']}")
                elif data.get("payload", {}).get("data") and encryption_key:
                    decrypted = decrypt_data(data["payload"]["data"], encryption_key)
                    print("decrypted payload data:")
                    print(json.loads(decrypted))
            except Exception:
                print(" Error decrypting payload.data - check ENCRYPTION_KEY")
    except Exception as e:
        print(f"Error printing message: {e}")


class ESSConsumer:
    def __init__(self, stream_name=None, durable_name=None):
        self.nc = None
        self.js = None
        self.consumer = None
        self.servers = [ESS_SERVER] if ESS_SERVER else ["localhost:4222"]
        self.stream_name = stream_name or ESS_STREAM_NAME
        self.durable_name = durable_name or os.getenv("ESS_DURABLE_NAME", str(uuid.uuid4()))
        self.encryption_key = ESS_ENCRYPTION_KEY
        self.source_filter = ESS_SOURCE_FILTER or False
        self.localhost = ESS_LOCALHOST

    async def connect(self):
        if self.nc and self.nc.is_connected:
            return
        try:
            if ESS_NKEY_SEED:
                logger.info("Connecting to ESS using NKey authentication")
            else:
                logger.info("Connecting to ESS without authentication (NKey seed not set)")
            self.nc = await nats.connect(
                servers=self.servers,
                nkeys_seed=ESS_NKEY_SEED,
                reconnect_time_wait=10,
            )
            self.js = self.nc.jetstream()
            jsm = await self.js.jetstream_manager()
            await jsm.consumers.add(
                self.stream_name,
                {
                    "ack_policy": AckPolicy.Explicit,
                    "durable_name": self.durable_name,
                },
            )
            self.consumer = await self.js.consumers.get(self.stream_name, self.durable_name)
        except Exception as e:
            logger.error(f"Failed to connect to ESS: {e}")
            raise

    async def create_stream(self):
        try:
            # Use admin credentials if provided, otherwise use NKey or no auth
            if ESS_ADMIN_USER and ESS_ADMIN_PASSWORD:
                logger.info("Establishing connection with admin credentials for stream creation...")
                connect_kwargs = {
                    "servers": self.servers,
                    "reconnect_time_wait": 10,
                    "user": ESS_ADMIN_USER,
                    "password": ESS_ADMIN_PASSWORD,
                }
            elif ESS_NKEY_SEED:
                logger.info("Establishing connection with NKey for stream creation...")
                connect_kwargs = {
                    "servers": self.servers,
                    "nkeys_seed": ESS_NKEY_SEED,
                    "reconnect_time_wait": 10,
                }
            else:
                logger.info("Establishing connection without authentication for stream creation...")
                connect_kwargs = {
                    "servers": self.servers,
                    "reconnect_time_wait": 10,
                }

            admin_nc = await nats.connect(**connect_kwargs)
            admin_js = admin_nc.jetstream()
            admin_jsm = await admin_js.jetstream_manager()
            logger.info(f'Checking if stream "{self.stream_name}" exists...')
            streams = await admin_jsm.streams.list().next()
            stream_exists = any(s.config.name == self.stream_name for s in streams)
            if not stream_exists:
                logger.info(f'Stream "{self.stream_name}" does not exist. Creating it...')
                await admin_jsm.streams.add(
                    name=self.stream_name,
                    subjects=ESS_FILTER_SUBJECTS,
                    retention="limits",
                    max_msgs=-1,
                    max_bytes=-1,
                    max_age=0,
                    storage="file",
                    num_replicas=1,
                )
                logger.info(f'Stream "{self.stream_name}" created successfully.')
            else:
                logger.info(f'Stream "{self.stream_name}" already exists.')
            await admin_nc.close()
        except Exception as e:
            logger.error(f"Error creating stream: {e}")
            raise

    async def pull(self):
        try:
            messages = await self.consumer.fetch(
                filter_subjects=ESS_FILTER_SUBJECTS,
                max_messages=ESS_MAX_MESSAGES,
            )
            async for m in messages:
                print_msg(m, self.encryption_key, self.source_filter)
                await m.ack()
        except JetStreamError as e:
            logger.error(f"JetStream error while fetching messages: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while pulling messages: {e}")
            raise

    async def run(self):
        await self.connect()
        while True:
            try:
                await self.pull()
            except NatsTimeout:
                logger.debug("No messages received within timeout, continuing...")
                pass

    async def shutdown(self):
        print("\nshutdown...")
        if self.nc:
            await self.nc.drain()


async def main():
    consumer = ESSConsumer()
    try:
        await consumer.run()
    except KeyboardInterrupt:
        await consumer.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
