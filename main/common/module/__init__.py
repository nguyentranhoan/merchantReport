from common.module.amqp_provider import AMQPProvider
from common.module.config_provider import ConfigProvider
from common.module.consul_client_provider import ConsulClientProvider
from common.module.consumers_provider import ConsumerProvider
from common.module.controllers_provider import ControllerProvider
from common.module.executor_provider import ThreadExecutorProvider
from common.module.fast_api_provider import FastAPIProvider
from common.module.interceptor_provider import InterceptorProvider
from common.module.mongo_client_provider import MongoClientProvider
from common.module.redis_provider import RedisProvider

modules = [ConfigProvider,
           MongoClientProvider,
           ConsulClientProvider,
           InterceptorProvider,
           FastAPIProvider,
           AMQPProvider,
           RedisProvider,
           ControllerProvider,
           ConsumerProvider,
           ThreadExecutorProvider]
