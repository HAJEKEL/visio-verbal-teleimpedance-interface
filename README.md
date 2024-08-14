# visio-verbal-teleimpedance-interface

This software is tested on google chrome, so dont use a different browser. The frontend uses javascript with react whereas the backend is written using python. The backend uses fastapi to build the rest api. REST stands for representational state transfer, which is a standardized software architecture style. They are all about communication between client and server. A restful web service is a service that uses REST APIs to communicate. REST is standardized and industry used, no need to worry about formatting data or formatting requests. They are also scalable and stateless, you dont have to worry about what data is in which state. They have also high performance due to their cache support.

This creates url's that we can call, when we call the url's we receive a response. It allows us to send messages using the openai API to openai. For example, using fastapi we can send an audio file to openai using its api and receive back the transcription of the audio. We then send this received transcription to another url and receive back the gpt 4 vision response. We then send this response to another url which turns back the audio file that contains the gpt 4 vision response in human voice.

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

## Frontend

To make the app interactive I used excalidraw to make the wireframe.
The frontend is build using react where everything is a component. It uses jsx which allows html-like code within javascript to write the components. React is a web framework that uses Javascript. It is created and maintained by Facebook with the library being open source.

A component is an aspect of your user interface. Components in react are reusable.

With jsx we can write functions with javascript that return html like code.

For styling I use Tailwind because then I dont need to write a css style sheet for each component. It speeds up development time.

Traditionally you would have html with a body tag, a style tag with a .name and a div tag that would apply the .name style class.  
The style class can be reused.

With tailwind you can apply a style class with className, and then write all the styling in line. This removes the reusability of style classes, but it simplifies the process as you dont need to make style sheets for each component of the code. It's a way to quickly get something going.

## VSCODE

To code this I used vscode, I used the plugins Auto Close Tag, such that I dont need to write the closing tags myself when writing the html code. I also used the auto rename tag plugin, that automatically adjusts the write's the close tag name when I write the open tag name. I also used the plugin ES7+ React/redux/react-Native snippets such that I dont need to write the whole react functions as the snippets already give a template for react functions. I also use Prettier to automatically neat up my code after each save. I also use the vscode plugin called Isort to sort the python imports automatically. I also have intelliSense for python. And also Tailwind css intellisense. Intellisense shows you what it thinks you want to type next when coding.

## Docker

I'm using docker for this application. Where a VM or virtual machine as a way to simulate a computer inside a computer by slicing of a bit of your RAM a bit of your harddrive and some cpu processing time

### Computer memory

Everything in the computers memory takes the form of bits or binary digits, each bit is stored in a memory cell that can switch between two states 0 and 1. Files and programs consist of milions of these bits. They are processed in the central processing unit (CPU), which acts as the computers brain. Computers have short term memory for imidiate tasks and long term memory for more permanent storage. When you run a program, the operating system allocates area within the short-term memory for performing those instructions. The memories latency refers to the time it takes for the cpu to read information from or write information to the short term memory. The short term memory is called random access memory RAM because the short term memory can be accessed in any order. DRAM or dynamic RAM consists of cells with a tiny transistor and a capacitor. The capacitor stores electrical charge. Charged means 1 while no charge means 0. DRAM requires periodic recharging because the capacitors leak charge over time. The transistor acts as a switch that controls access to the capacitor. For write operations the transistor is turned on to place a charge on the capacitor, for read operation the transistor is turned on to measure the charge in the capacitor.

Transistors acts as a switch. For DIY projects you have transistors that consist of 3 pins, the emitter, base and the collector.

However, for computers, transistors are produced on nano scale. They are made with silicon. Silicon can be made a semi-conductor. They redily form covalent bonds with 4 other silicon atoms to form a cristal structure as they all want 8 electrons in the outer shell to be most stable. You can add impurities like phosforous to get n-type due to the extra electron as it has 5 electrons in its valent shell. It makes the n-type negatively charged as it the electrons can freely roam the structure. The ptype is doped with boron which only has 3 electrons in its valent shell. It has moving holes so to say and it is therefore positively charged as it net electrons are missing. Arranging these N and P types in an N-P-N structure and connect terminals to each, we've created the most common transistor.
