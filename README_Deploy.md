# Deployment🚀
Welcome to the setup guide for deploying RVC project!
Follow these steps to get started smoothly.

## Setup `.env` file: 

- Create `.env` file:

    ```shell
    cp .env.template .env
    ```

- Modify service ports in `.env` file if necessary:

    ```
    RVC_PORT=7866
    RVC_WEBUI_PORT=7865
    ```

- Specify path for Charspeak project's storage folder:

    ```shell
    CHARSPEAK_STORAGE_DIR=/path/to/charspeak/storage/dir
    ```

## Run service(s):
   
 - If only the `api` service is needed:

     ```shell
   docker compose up api -d
     ```

 - Full deployment:

     ```shell
   docker compose up -d
     ```
   
    **_NOTES:_** Keep an eye on the magic by using `docker compose logs api -f` to monitor logs in real time.

Happy deploying! 🚀✨