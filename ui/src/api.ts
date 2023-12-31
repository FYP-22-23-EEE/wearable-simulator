import axios from "axios";
import {AxiosInstance} from "axios";

let _client: AxiosInstance;

async function getClient() {
    if (_client) {
        return _client;
    }
    const response = await axios.get(`/config`);
    console.log("config", response.data);
    const config = response.data;

    _client = axios.create({
        baseURL: config.url,
    });
    return _client;
}

const api = {
    getState: async () => {
        const client = await getClient();
        const response = await client.get("/api/state");
        return response.data;
    },
    setActivity: async (activity: string) => {
        const client = await getClient();
        const response = await client.post("/api/activity", {activity});
        return response.data;
    },
    setDeviceState: async (device: string, state: boolean) => {
        const client = await getClient();
        const response = await client.post("/api/device/state", {device, state});
        return response.data;
    }
}

export default api;