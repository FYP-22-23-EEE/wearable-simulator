# Start with a Node.js image for the React build
FROM node:16.20.0-alpine3.18 as build

WORKDIR /usr/src/app

# Copy package.json and package-lock.json before other files for caching
COPY ui/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY ui/ .

# Build the frontend
RUN npm run build

# Start a new stage with python image
FROM python:3.11-slim

WORKDIR /usr/src/app

# Copy requirements.txt and install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code except ui
COPY device ./device
COPY app ./app
COPY main.py ./

# Copy the frontend build from the previous stage
COPY --from=build /usr/src/app/dist ./ui/dist

ENV APP_HOST=localhost
ENV APP_PORT=5000
ENV APP_PUBLIC_URL='http://localhost:5000'

# Run the application
CMD [ "python", "./main.py" ]
