import errno
import discord
import pymongo

from sigma.core.mechanics.database import Database
from sigma.core.mechanics.config import load_config
from sigma.core.mechanics.logger import create_logger
from sigma.core.mechanics.command import PluginManager


class ApexSigma(discord.AutoShardedClient):
    def __init__(self):
        super().__init__()
        self.init_logger()
        self.log.info('---------------------------------')
        self.init_config()
        self.log.info('---------------------------------')
        self.init_database()
        self.log.info('---------------------------------')
        self.init_modules()

    def init_logger(self):
        self.log = create_logger('Sigma')
        self.log.info('Logger Created')

    def init_config(self):
        self.log.info('Loading Configuration...')
        self.cfg = load_config()
        self.log.info('Configuration Loaded')

    def init_database(self):
        self.log.info('Connecting to Database...')
        self.db = Database(self.cfg.db)
        try:
            self.db.test.collection.find_one({})
        except pymongo.errors.ServerSelectionTimeoutError:
            self.log.error('A Connection To The Database Host Failed!')
            exit(errno.ETIMEDOUT)
        except pymongo.errors.OperationFailure:
            self.log.error('Database Access Operation Failed!')
            exit(errno.EACCES)
        self.log.info('Successfully Connected to Database')

    def init_modules(self):
        self.log.info('Loading Sigma Modules')
        self.modules = PluginManager(self)

    def run(self):
        try:
            self.log.info('Connecting to Discord Gateway...')
            super().run(self.cfg.dsc.token, bot=self.cfg.dsc.bot)
        except discord.LoginFailure:
            self.log.error('Invalid Token!')
            exit(errno.EPERM)

    async def on_ready(self):
        self.log.info('---------------------------------')
        self.log.info('Connection to Discord Established')
        self.log.info(f'User Account: {self.user.name}#{self.user.discriminator}')
        self.log.info(f'User Snowflake: {self.user.id}')
        self.log.info('---------------------------------')

    async def on_message(self, message):
        if message.content.startswith(self.cfg.pref.prefix):
            args = message.content.split(' ')
            cmd = args.pop(0)[len(self.cfg.pref.prefix):].lower()
            if cmd in self.modules.commands:
                await self.modules.commands[cmd].execute(message, args)

