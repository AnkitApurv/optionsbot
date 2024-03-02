# Options Trading Bot

## Goal: Automated day trading

## Objectives

1. Fetch realtime market data from various web services
2. Evaluating tickers according to strategies.
3. Executing trades according to strategy recommendations on various trading platforms
4. Providing information about these trades to the user at one web location.

## Architecture

App will have multiple, completely independent components:

- trading algorithm
  - platform agnostic
  - capable of being instantiated - one instance per trading platform and account, representing one trading agent
  - will subscribe to stream of incoming ticker data
  - will publish signals to buy/sell calls and puts
  - responsible for trade decision making, hence needs to be aware of current trades which have been made by it's representative trading agent
- trading platform interactor
  - one implementation per trading platform
  - responsible for providing a generic interface to rest of the app to
    - login to trading platform using credentials
    - accept app's internal buy/sell signals and forward it to trading platform
- market data provider
  - one implementation per ticker data provider
  - this can either be a trading platform or an independent service
- representative agent
  - trading platform, algorithm, and market data provider agnostic
  - brings trading algorithm, trading platform interactor and market data provider together to actually act as a coherent trading agent
- recipe configs for representative agent
  - config files describing combination of following which will form an instance of a representative agent
    - trading platform's user id
    - algorithm
    - market data provider
  - one config file per agent
- meta agents manager
  - will provide guardrails against problems which can occur when multiple agents are at play, for example:
    - preventing use of one trading platform's user id in multiple representative agents
    - instantiating agents
    - monitoring and reporting on agents' health

## Implementation Specifics

- Interaction between components - publish subscribe model
  - [ZeroMQ](https://zeromq.org/)
  - [blinker](https://pypi.org/project/blinker/)
    - [reference](https://stackoverflow.com/questions/1092531/which-python-packages-offer-a-stand-alone-event-system)
- Secrets storage - [keyring](https://pypi.org/project/keyring/)
- Data Storage
  - during runtime - [Redis](https://redis.io/)
  - persistence
    - config - yaml
    - tabular data store - parquet
- DataFrames - [polars](https://pola.rs/)
- Authentication - Password less - [FIDO2 WebAuthn](https://pypi.org/project/webauthn/) - This can be made unnecessary if a way can be figured out to easily encrypt secrets without programmer's manual intervention. Not possible! Make a web form in which user cn write details of new credentials, which will then be saved in keyring, another page where those credentials can be listed and deleted
- Type Safety:
  - mypy
  - [Pydantic](https://docs.pydantic.dev/latest/)
  - [Result](https://pypi.org/project/result/)
- Datetime - [Pendulum](https://pendulum.eustace.io/)

For user auth: replace with pywebio with basic auth for auth + pgp (using gnupg) + mozilla sops for saving password etc

For secrets management:

replace with either of the two

- for central sotre serving multiple remote deployments -> hashicorp vault [not recommended dure to extra dependencies and need to manage secure connection b/w this vault and deployemnt which needs to use it's sevice]
- for a mechnism isolated to an individual deployment -> pgp (using gnupg) + mozilla sops

Where's the documentation?
Uses materials for mkdocs
