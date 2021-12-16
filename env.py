import os

def getenv(env_var):
  env_value = os.getenv(env_var, "").strip()
  if not env_value:
    raise Exception("invalid app setup")
  return env_value
