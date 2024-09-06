from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


class DatabaseSettings(Settings):
    DRIVER: str
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    PORT: str
    NAME: str

    class Config:
        env_prefix: str = 'DATABASE_'

    @property
    def url(self) -> str:
        driver, user, password, host, port, name = (
            self.DRIVER,
            self.USERNAME,
            self.PASSWORD,
            self.HOSTNAME,
            self.PORT,
            self.NAME,
        )

        return f'{driver}://{user}:{password}@{host}:{port}/{name}'


database_settings = DatabaseSettings()
