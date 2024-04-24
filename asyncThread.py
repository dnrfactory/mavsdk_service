import logging
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import asyncio
import queue

logger = logging.getLogger()


class AsyncThread(QThread):
    data_received = pyqtSignal()
    instance = None

    def __init__(self):
        super().__init__()

        self._queue = queue.Queue()

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = AsyncThread()
        return cls.instance

    def put(self, item):
        self._queue.put(item)

    async def main(self):
        while True:
            logger.debug('.')
            # task = self._queue.get()
            # await asyncio.sleep(1)

            try:
                data = self._queue.get(timeout=1)
            except queue.Empty:
                logger.debug('queue.Empty')
                await asyncio.sleep(0.1)
                continue

            logger.debug(f'data: {data}')
            if data is None:
                break
            method, args = data
            logger.debug(f'method: {method}')
            logger.debug(f'args: {args}')
            await method(*args)
            logger.debug('*')

    def run(self):
        asyncio.run(self.main())

        self.quit()