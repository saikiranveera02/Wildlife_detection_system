import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, AlertTriangle, CheckCircle, Video, Activity } from 'lucide-react';

const API_BASE_URL = 'https://qkzpmdfc6f.us-east-1.awsapprunner.com/api';

const Dashboard = () => {
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isWebcamMode, setIsWebcamMode] = useState(false);
    const [isVideoActive, setIsVideoActive] = useState(false);
    const [alerts, setAlerts] = useState([]);

    // Poll for new alerts every 2 seconds if video is active
    useEffect(() => {
        let interval;
        if (isVideoActive) {
            interval = setInterval(async () => {
                try {
                    const res = await axios.get(`${API_BASE_URL}/alerts`);
                    if (res.data.alerts) {
                        setAlerts(res.data.alerts);
                    }
                } catch (err) {
                    console.error("Failed to fetch alerts", err);
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [isVideoActive]);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setIsVideoActive(false);
        setIsWebcamMode(false);
        setAlerts([]);
    };

    const handleWebcamMode = async () => {
        try {
            await axios.post(`${API_BASE_URL}/webcam/start`);
            setIsWebcamMode(true);
            setFile(null);
            setIsVideoActive(true);
            setAlerts([]);
        } catch (err) {
            console.error("Webcam activation failed", err);
            alert("Failed to start webcam. Is the backend running?");
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setIsWebcamMode(false);
            setIsVideoActive(true);
        } catch (err) {
            console.error("Upload failed", err);
            alert("Failed to upload video. Make sure the backend is running!");
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto">
            {/* Header */}
            <header className="mb-10 flex items-center justify-between border-b border-slate-800 pb-6">
                <div className="flex items-center space-x-4">
                    <div className="p-3 bg-emerald-500/10 rounded-xl">
                        <Activity className="w-8 h-8 text-emerald-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                            Wildlife Guardian System
                        </h1>
                        <p className="text-slate-400">AWS Powered AI Elephant Detection</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2 bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700">
                    <div className={`w-2.5 h-2.5 rounded-full ${isVideoActive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-500'}`}></div>
                    <span className="text-sm font-medium text-slate-300">
                        {isVideoActive ? 'System Active' : 'System Standby'}
                    </span>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Upload & Alerts */}
                <div className="space-y-8">
                    {/* Upload Card */}
                    <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-700/50 shadow-xl">
                        <h2 className="text-xl font-semibold mb-4 flex items-center">
                            <Upload className="w-5 h-5 mr-2 text-indigo-400" />
                            Upload Feed
                        </h2>

                        <div className="space-y-4">
                            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-600 border-dashed rounded-xl cursor-pointer bg-slate-800/50 hover:bg-slate-700/50 transition-colors">
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <Video className="w-8 h-8 mb-3 text-slate-400" />
                                    <p className="text-sm text-slate-300">
                                        <span className="font-semibold">Click to browse</span> or drag and drop
                                    </p>
                                    <p className="text-xs text-slate-500 mt-1">MP4, AVI, MOV</p>
                                </div>
                                <input type="file" className="hidden" accept="video/*" onChange={handleFileChange} />
                            </label>

                            {file && (
                                <div className="text-sm text-emerald-400 bg-emerald-400/10 p-3 rounded-lg flex items-center">
                                    <CheckCircle className="w-4 h-4 mr-2" />
                                    {file.name}
                                </div>
                            )}

                            <button
                                onClick={handleUpload}
                                disabled={!file || isUploading}
                                className={`w-full py-3 rounded-xl font-medium transition-all duration-300 flex justify-center items-center ${!file || isUploading
                                    ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                                    : 'bg-indigo-500 hover:bg-indigo-600 shadow-lg shadow-indigo-500/20 text-white'
                                    }`}
                            >
                                {isUploading ? (
                                    <span className="animate-pulse">Initializing System...</span>
                                ) : (
                                    <span>Start Live AI Scan</span>
                                )}
                            </button>

                            <div className="relative flex items-center py-2">
                                <div className="flex-grow border-t border-slate-700"></div>
                                <span className="flex-shrink mx-4 text-slate-500 text-xs uppercase font-bold tracking-widest">OR</span>
                                <div className="flex-grow border-t border-slate-700"></div>
                            </div>

                            <button
                                onClick={handleWebcamMode}
                                className={`w-full py-3 rounded-xl font-medium border-2 transition-all duration-300 flex justify-center items-center ${isWebcamMode
                                    ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400'
                                    : 'border-slate-700 text-slate-300 hover:border-emerald-500 hover:text-emerald-400'
                                    }`}
                            >
                                <Activity className="w-4 h-4 mr-2" />
                                Live Webcam Mode
                            </button>
                        </div>
                    </div>

                    {/* Alert History Card */}
                    <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl p-6 border border-slate-700/50 shadow-xl">
                        <h2 className="text-xl font-semibold mb-4 flex items-center">
                            <AlertTriangle className="w-5 h-5 mr-2 text-rose-400" />
                            AWS Alert Log
                        </h2>

                        <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                            {alerts.length === 0 ? (
                                <div className="text-center text-slate-500 py-8 border border-slate-700/50 rounded-xl border-dashed">
                                    No alerts detected yet.
                                </div>
                            ) : (
                                alerts.slice().reverse().map((alert, idx) => (
                                    <div key={idx} className="bg-rose-500/10 border border-rose-500/20 p-4 rounded-xl flex items-start space-x-3 animate-in fade-in slide-in-from-top-4 duration-300">
                                        <div className="mt-0.5 animate-pulse">
                                            <AlertTriangle className="w-5 h-5 text-rose-400" />
                                        </div>
                                        <div>
                                            <h4 className="text-rose-400 font-semibold">{alert.message}</h4>
                                            <div className="flex items-center space-x-2 mt-1 text-sm text-slate-400">
                                                <span>{alert.timestamp}</span>
                                                <span>•</span>
                                                <span>AWS Lambda Triggered</span>
                                                <span>•</span>
                                                <span>SNS Email Sent</span>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Column: Live Video Feed */}
                <div className="lg:col-span-2 space-y-4">
                    <div className="bg-slate-800/50 backdrop-blur-xl rounded-2xl overflow-hidden border border-slate-700/50 shadow-xl min-h-[500px] flex flex-col">
                        <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-slate-800/80">
                            <h2 className="font-semibold flex items-center text-slate-200">
                                <Video className="w-5 h-5 mr-2 text-cyan-400" />
                                Live Inference Stream
                            </h2>
                            {isVideoActive && (
                                <span className="flex items-center px-3 py-1 bg-rose-500/20 text-rose-400 rounded-full text-xs font-bold uppercase tracking-wider animate-pulse">
                                    <span className="w-2 h-2 rounded-full bg-rose-500 mr-2"></span>
                                    Live AI Processing
                                </span>
                            )}
                        </div>

                        <div className="flex-1 bg-black relative flex items-center justify-center">
                            {!isVideoActive ? (
                                <div className="absolute inset-0 flex flex-col justify-center items-center text-slate-600 bg-slate-900/50">
                                    <Video className="w-16 h-16 mb-4 opacity-50" />
                                    <p className="text-lg font-medium">Camera Feed Offline</p>
                                    <p className="text-sm mt-2 opacity-75">Upload a video to start the AI engine.</p>
                                </div>
                            ) : (
                                <img
                                    src={`${API_BASE_URL}/video_feed?t=${Date.now()}`}
                                    alt="Live Inference Feed"
                                    className="w-full h-full object-contain"
                                />
                            )}
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Dashboard;
