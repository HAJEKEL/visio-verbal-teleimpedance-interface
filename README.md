# visio-verbal-teleimpedance-interface

This software is tested on google chrome, so dont use a different browser. The frontend uses javascript with react whereas the backend is written using python. The backend uses fastapi to build the rest api. This creates url's that we can call, when we call the url's we receive a response. It allows us to send messages using the openai API to openai. For example, using fastapi we can send an audio file to openai using its api and receive back the transcription of the audio. We then send this received transcription to another url and receive back the gpt 4 vision response. We then send this response to another url which turns back the audio file that contains the gpt 4 vision response in human voice.

## Backend code structure

main.py

- Imports
- CORS: cross-origin resource sharing. This allows the frontend to talk to the backend. Security can be set-up to do so.
- /heath entrypoint: A checkpoint to see if everything is up and running.
- API Route Endpoint: this will be called post_audio. Here we will send an audio file.

1. First it saves the audio input,
2. it will then convert the audio to text (OpenAI Whisper),
3. it will then get the chatbot response (OpenAI gpt 4 vision), 4. it will then add that response to the chat history such that gpt can build up the context of the specific task it needs to solve as a visio-verbal tele-impedance interface.
4. The response is also send to the text-to-speech api of OpenAI to generate the human voice audio file of the response.

## Requirements

This software is tested on google chrome, so dont use a different browser. The frontend uses javascript with react whereas the backend is written using python. The backend uses fastapi to build the rest api. This creates url's that we can call, when we call the url's we receive a response. It allows us to send messages using the openai API to openai. For example, using fastapi we can send an audio file to openai using its api and receive back the transcription of the audio. We then send this received transcription

## The frontend uses react and typescript

We've created the frontend-react folder using:
yarn create vite
Typescript is the same as javascript including types. So you can make use of the types during programming if you feel like.

package.json manages all the packages and code libraries that are being downloaded. We have added axios to make web requests using:
yarn add axios
