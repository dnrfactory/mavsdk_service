import logging
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import asyncio
import queue
import time

logger = logging.getLogger()


class AsyncThread(QThread):
    data_received = pyqtSignal()
    instance = None

    def __init__(self):
        super().__init__()

        self._queue = queue.Queue()
        self._timeStamp = time.time()

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = AsyncThread()
        return cls.instance

    def put(self, item):
        self._queue.put(item)

    def putFinishMsg(self):
        logger.debug('')
        self._queue.put('finish')

    async def main(self):
        while True:
            currentTime = time.time()
            # logger.debug(f'curr: {currentTime}')
            # logger.debug(f'prev: {self._timeStamp}')
            if currentTime - self._timeStamp > 3:
                self._timeStamp = time.time()
                # logger.debug('.')

            try:
                data = self._queue.get(block=False)
            except queue.Empty:
                # logger.debug('queue.Empty')
                await asyncio.sleep(0.01)
                continue

            logger.debug(f'data: {data}')
            if data is None:
                break
            if data == 'finish':
                break
            method, args = data
            logger.debug(f'method: {method}')
            logger.debug(f'args: {args}')
            # try:
            await method(*args)
            # except TypeError as e:
            #     logger.debug(f'error: {e}')

    def run(self):
        asyncio.run(self.main())

        self.quit()