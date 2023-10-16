class Cache:
    MANAGER_USERS_CACHE_KEY = "MANAGER_USERS"

    TIMEOUT_A_DAY = 60 * 60 * 24  # a day

    ACCESS_LOG_CACHE_KEY = "{ip}_{username}"
