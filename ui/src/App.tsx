import React from 'react'
import muse from './assets/muse.png'
import zephyr from './assets/zephyr.png'
import e4 from './assets/e4.png'
import earbuds from './assets/earbuds.png'
import api from "./api.ts";


interface DeviceCardProps {
    name: string
    image: any
}

function DeviceCard({name, image}: DeviceCardProps) {
    const [checked, setChecked] = React.useState(false)

    React.useEffect(() => {
        (async function () {
            const state = await api.getState();
            if (state && state.devices && state.devices[name.toLowerCase()]) {
                setChecked(true)
            } else {
                setChecked(false)
            }
        })();
    }, [])

    const onToggle = async () => {
        await api.setDeviceState(name.toLowerCase(), !checked)
        setChecked(!checked)
    }

    return (
        <div className="card w-full aspect-content aspect-[1/1] bg-base-100 shadow-xl image-full">
            <figure>
                <img src={image} alt="earbuds"/>
            </figure>
            <div className="card-body">
                <h2 className="card-title mb-0">{name}</h2>
                <p className="text-sm">{checked ? 'Running' : 'Stopped'}</p>
                <div className="card-actions justify-end">
                    <div className="form-control">
                        <label className="label cursor-pointer">
                            <input type="checkbox" className="toggle" checked={checked}
                                   onChange={onToggle}/>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ActivitySelect() {
    const [activity, setActivity] = React.useState('IDLE')

    React.useEffect(() => {
        (async function () {
            const state = await api.getState();
            if (state && state.activity) {
                setActivity(state.activity.toUpperCase())
            }
        })();
    }, [])

    const onChange = async (e: any) => {
        setActivity(e.target.value)
        await api.setActivity(e.target.value.toLowerCase())
    }

    return (
        <div className="form-control w-full">
            <label className="label">
                <span className="label-text">Activity:</span>
            </label>
            <select className="select select-bordered select-lg" value={activity}
                    onChange={onChange}>
                <option>IDLE</option>
                <option>WALKING</option>
                <option>RUNNING</option>
            </select>
        </div>
    )
}

function App() {

    return (
        <div className="min-h-screen bg-amber-50 w-screen flex flex-col justify-center items-center ">
            <div className="w-[400px]">
                <div className="w-full mb-4">
                    <ActivitySelect/>
                </div>

                <div className="grid grid-cols-2 gap-4 justify-center">
                    <DeviceCard name='E4' image={e4}/>
                    <DeviceCard name='EARBUDS' image={earbuds}/>
                    <DeviceCard name='MUSE' image={muse}/>
                    <DeviceCard name='ZEPHYR' image={zephyr}/>
                </div>
            </div>
        </div>
    )
}

export default App
