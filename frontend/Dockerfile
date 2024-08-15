# Use an official Node.js runtime as a parent image, which includes npm
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy the existing package.json file into the container
COPY package.json ./

# Install dependencies
RUN yarn install

# Copy the rest of the application code into the container
COPY . .

# Expose the application port
EXPOSE 3000

# Start the development server
CMD ["yarn", "dev"]