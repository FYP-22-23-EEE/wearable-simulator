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
FROM python:3.10-slim

WORKDIR /usr/src/app

# Copy requirements.txt and install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code except ui
COPY device ./device
COPY main.py ./
COPY app/__init__.py ./

# Copy the frontend build from the previous stage
COPY --from=build /usr/src/app/dist ./ui/dist

# Run the application
CMD [ "python", "./main.py" ]
