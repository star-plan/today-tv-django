from config.settings.components.common import DOCKER

# Q_CLUSTER = {
#     'name': 'today_tv',
#     'workers': 4,
#     'recycle': 500,
#     'timeout': 60,
#     'compress': True,
#     'cpu_affinity': 1,
#     'save_limit': 250,
#     'queue_limit': 500,
#     'label': 'Django Q',
#     'redis': {
#         'host': 'redis' if DOCKER else 'localhost',
#         'port': 6379,
#         'db': 2,
#     }
# }

Q_CLUSTER = {
    'name': 'DjangORM',
    'workers': 4,
    'timeout': 90,
    'retry': 120,
    'queue_limit': 50,
    'bulk': 10,
    'orm': 'qcluster'
}