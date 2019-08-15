Title: 一个 Python 小项目的小结
Date: 2019-08-14
Author: xiayf
Slug: a-python-project-summary
Tags: 总结, Python

前段时间临时接手一个 Python 小项目，这个项目实现的类似一个管控平台，其中核心功能是为算法同学提供机器学习模型训练任务的全流程管理，平台后端基于 Flask 框架实现，前端基于 Ant Design Pro 实现。

代码稍微有些乱，所以做了部分代码的重构，在此做点经验小结。

### 1、部分请求处理逻辑，由于比较耗时，故使用线程池来加速，或者使用独立线程异步处理，或者先存储一个中间状态，由后台定时任务来完成实际的处理工作。对于异步处理结果，前端通过轮询来获取。

线程池的使用，主要使用 map 方法：

```python
from multiprocessing.dummy import Pool

input_list = [...]
pool: Pool = Pool(len(input_list))
pool.map(func, input_list)
pool.close()
pool.join()
```

独立线程异步处理：

```python
import multiprocessing

p = multiprocessing.Process(target=func, args=(...))
p.start()
```

定时任务，基于 apscheduler 库实现：

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

scheduler.add_join(func, 'interval', seconds=1)

scheduler.start()
```

因为对于 Python 应用，通常会使用 gunicorn 这种 WSGI HTTP 服务器以多进程启动多个应用实例，提升请求吞吐能力。但是对于定时任务我们希望只有一个实例，对此，如果使用 gunicorn，可以基于它的 preload 机制来实现：

```python
# wsgi.py
import app

if __name__ == "__main__":
    app.run()
```

```
# 注意其中的 --preload 参数
gunicorn --workers=4 --preload --log-level=info --access-logfile=access.log -b 0.0.0.0:8080 wsgi:app
```

preload 机制简单来说，就是 import app 类所在的模块及其依赖的各个模块（import 过程中会执行其中的语句），然后 fork 出多个进程，每个进程都执行 app.run()。

### 2、实现一些通用方案对异常进行捕获或重试

```python
def exception_try(times: int = 3, sleep_then_try_seconds=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            count = 0
            exception = None
            while count < times:
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    exception = e
                    count += 1
                    logging.exception("Try {} times".format(count))
                    if (sleep_then_try_seconds is not None) and count < times:
                        time.sleep(sleep_then_try_seconds)
            raise exception
        return wrapper
    return decorator
```

```python
@exception_try(times=3, sleep_then_try_seconds=0.5)
def connect(self):
    return pymysql.connect(host=self.host, user=self.user, password=self.password, db=self.db, charset=self.charset)
```

这个装饰器方法用于实现异常重试，并且可以指定重试的时间间隔，实际使用下来效果较好。而且也不会因为 `try...except` 导致大块代码缩进。

**确保数据库连接关闭（其它类似资源也可以这样实现）**

```python
def with_db(db: Connection, exception_callback=None):
    def decorator(f):
        def db_context(*a, **kw):
            try:
                return f(db, *a, **kw)
            except Exception as e:
                logging.exception(str(e))
                if exception_callback is not None:
                    exception_callback(e)
            finally:
                try:
                    db.close()
                except:
                    pass
        return db_context

    return decorator
```

```python
# 将 conf.db.connect() 对象作为 delete_task_from_job_queue 的第一个参数注入，task_id 这个参数以不定参数的方式传入 delete_task_from_job_queue
with_db(conf.db.connect())(delete_task_from_job_queue)(task_id)
```

这个装饰器方法用于确保数据库连接在异常发生也能正常关闭，防止资源泄露。

### 3、循环等待或超时

```python
class TimeoutCondition(object):

    def __init__(self, condition_func, timeout_seconds):
        self.condition = condition_func
        self.timeout = timeout_seconds
        self.begin = None
        self.timeout_false = True
        self.cond_true = True

    def __bool__(self):
        if self.begin is None:
            self.begin = timeit.default_timer()
        self.cond_true = self.condition()
        self.timeout_false = self.timeout <= 0 or (timeit.default_timer() - self.begin) < self.timeout
        return self.cond_true and self.timeout_false

    def is_timeout(self):
        return self.cond_true and not self.timeout_false
```

```python
cond = TimeoutCondition(lambda : len(service_list) == 0, 5)
while cond:
    time.sleep(1)
    service_list = get_service_list()
if cond.is_timeout():
    return None, None
```

`TimeoutCondition` 用于实现循环等待某个条件满足，但为了避免死循环，所以加一个超时条件判断。实例化参数第一个是原始的条件判断 lambda 语句，第二个是一个超时设置。另外，借助魔术方法 `__bool__`，让 TimeoutCondtion 的实例用起来像是一个布尔变量，调用 `is_timeout()` 方法可以区分循环等待退出是因为原始条件满足，还是超时退出的。

### 4、按部署环境配置应用的行为

应用在不同的环境（开发、测试、生产）中应该允许加载不同的配置，配置不同的行为。

当前应用处于什么环境，可以通过环境变量来配置，应用初始化时最先检测当前处于什么环境，之后的初始化流程就可以依据环境配置来加载配置，定制应用行为。

```python
# conf/__init__.py
class AppConfig(object):
    app_env = os.getenv('APP_ENV', 'development')
    is_prod = app_env == 'production'
    is_dev = app_env == 'development'
    is_testing = app_env == 'testing'
    
    # 其余应用配置项
    ...

conf = AppConfig()


def _load_config_by_env(env: str):
    '''
    不同环境加载不同的配置文件
    配置目录结构：
    conf/
        __init__.py
        development.py
        production.py
        testing.py
    '''
    module = importlib.import_module('conf.{}'.format(env))
    if not hasattr(module, 'Config'):
        logging.warning('Not find {} config'.format(env))
        return
    for name, value in getattr(module, 'Config').__dict__.items():
        if name.startswith('__'):
            continue
        conf.__dict__[name] = value
```

```python
# 根据环境配置日志级别
log_level = logging.INFO if conf.is_prod else logging.DEBUG
logging.basicConfig(format=consts.LOG_FORMAT, level=log_level)
```
