'use client';

import { useState } from 'react';
import {
    Sparkles,
    Lightbulb,
    Search,
    Loader,
    ArrowRight,
    User,
    Users,
    MessageSquare,
    Image as ImageIcon,
    Video as VideoIcon,
    Download,
    Copy,
    Check,
    Volume2,
    Play
} from 'lucide-react';
import toast from 'react-hot-toast';
import { apiClient } from '@/lib/api-client';
import clsx from 'clsx';

interface Idea {
    id: string;
    title: string;
    description: string;
    style: string;
}

interface Scene {
    scene_number: number;
    dialogue: string;
    background: string;
    visual_description: string;
    video_prompt: string;
    image_url?: string;
    audio_url?: string;
}

interface FullScript {
    title: string;
    thumbnail_prompt: string;
    scenes: Scene[];
}

export function StudioFeature() {
    const [topic, setTopic] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [ideas, setIdeas] = useState<Idea[]>([]);
    const [selectedIdea, setSelectedIdea] = useState<Idea | null>(null);

    const [isGeneratingScript, setIsGeneratingScript] = useState(false);
    const [script, setScript] = useState<FullScript | null>(null);
    const [isGeneratingImage, setIsGeneratingImage] = useState<Record<number, boolean>>({});
    const [isGeneratingAudio, setIsGeneratingAudio] = useState<Record<number, boolean>>({});
    const [isExporting, setIsExporting] = useState(false);

    const [charConfig, setCharConfig] = useState({
        role: 'Bà và cháu gái',
        addressing: 'Bà - Cháu',
        style: '3D Animation'
    });

    const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

    const characterProfiles = [
        { key: 'grandparent_and_child', name: 'Bà và cháu gái', icon: Users },
        { key: 'entrepreneur', name: 'Doanh nhân trẻ', icon: User },
        { key: 'chef', name: 'Đầu bếp chuyên nghiệp', icon: User },
        { key: 'student', name: 'Sinh viên năng động', icon: User },
    ];

    const handleSearchIdeas = async () => {
        if (!topic.trim()) {
            toast.error('Vui lòng nhập chủ đề');
            return;
        }

        try {
            setIsSearching(true);
            setIdeas([]);
            setScript(null);
            setSelectedIdea(null);

            const result = await apiClient.getStudioIdeas(topic);
            if (result.success) {
                setIdeas(result.ideas);
                toast.success(`Tìm thấy ${result.ideas.length} ý tưởng độc đáo!`);
            }
        } catch (error) {
            toast.error('Lỗi khi tìm ý tưởng');
        } finally {
            setIsSearching(false);
        }
    };

    const handleSelectIdea = async (idea: Idea) => {
        setSelectedIdea(idea);

        try {
            setIsGeneratingScript(true);
            setScript(null);

            const result = await apiClient.generateStudioScript(idea.title, charConfig);
            if (result.success) {
                setScript(result);
                toast.success('Kịch bản chi tiết đã được tạo!');
            }
        } catch (error) {
            toast.error('Lỗi khi tạo kịch bản');
        } finally {
            setIsGeneratingScript(false);
        }
    };

    const handleGenerateImage = async (idx: number, visualDescription: string) => {
        try {
            setIsGeneratingImage(prev => ({ ...prev, [idx]: true }));
            const result = await apiClient.generateStudioImage(visualDescription, charConfig.role);

            if (result.success && result.image_url && script) {
                const newScenes = [...script.scenes];
                newScenes[idx].image_url = result.image_url;
                setScript({ ...script, scenes: newScenes });
                toast.success(`Ảnh cảnh ${idx + 1} đã được tạo!`);
            }
        } catch (error) {
            toast.error('Lỗi khi tạo ảnh AI');
        } finally {
            setIsGeneratingImage(prev => ({ ...prev, [idx]: false }));
        }
    };

    const handleGenerateAudio = async (idx: number, dialogue: string) => {
        try {
            setIsGeneratingAudio(prev => ({ ...prev, [idx]: true }));
            const result = await apiClient.generateStudioAudio(dialogue);

            if (result.success && result.audio_url && script) {
                const newScenes = [...script.scenes];
                newScenes[idx].audio_url = result.audio_url;
                setScript({ ...script, scenes: newScenes });
                toast.success(`Giọng đọc cảnh ${idx + 1} đã được tạo!`);
            }
        } catch (error) {
            toast.error('Lỗi khi tạo giọng nói AI');
        } finally {
            setIsGeneratingAudio(prev => ({ ...prev, [idx]: false }));
        }
    };

    const handleExportZip = async () => {
        if (!script) return;

        try {
            setIsExporting(true);
            const blob = await apiClient.exportStudioZip(script);

            const url = window.URL.createObjectURL(new Blob([blob]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `Studio_Project_${script.title.replace(/\s+/g, '_')}.zip`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            toast.success('Dự án đã được đóng gói và tải về!');
        } catch (error) {
            console.error(error);
            toast.error('Lỗi khi tải dự án (ZIP)');
        } finally {
            setIsExporting(false);
        }
    };

    const handleCopyPrompt = (text: string, index: number) => {
        navigator.clipboard.writeText(text);
        setCopiedIndex(index);
        toast.success('Đã sao chép Prompt!');
        setTimeout(() => setCopiedIndex(null), 2000);
    };

    return (
        <div className="relative min-h-screen space-y-16 pb-20 overflow-hidden font-outfit">
            {/* Background elements */}
            <div className="noise-overlay" />
            <div className="absolute top-0 left-0 w-full h-[500px] bg-gradient-to-b from-purple-900/10 to-transparent -z-10" />
            <div className="absolute -top-24 -right-24 w-96 h-96 bg-pink-600/10 rounded-full blur-[120px] -z-10 animate-pulse" />
            <div className="absolute top-1/2 -left-24 w-80 h-80 bg-blue-600/10 rounded-full blur-[100px] -z-10" />

            {/* Header / Search Section */}
            <section className="relative pt-12">
                <div className="max-w-4xl mx-auto px-4 text-center space-y-8">
                    <h1 className="text-7xl md:text-9xl font-black tracking-tighter uppercase leading-[0.8] italic font-syne animate-fade-in-up">
                        Story <br />
                        <span className="text-outline-neon">Studio</span>
                    </h1>
                    <p className="max-w-xl mx-auto text-lg text-gray-500 font-medium tracking-tight">
                        Transform raw ideas into high-fidelity AI-generated scripts and visuals.
                        The future of content creation is autonomous.
                    </p>

                    <div className="relative mt-12 group max-w-2xl mx-auto">
                        <div className="absolute -inset-1 bg-gradient-to-r from-purple-600/50 to-pink-600/50 rounded-2xl blur opacity-25 group-focus-within:opacity-75 transition duration-1000"></div>
                        <div className="relative flex items-center bg-black/60 backdrop-blur-3xl border border-white/10 rounded-2xl p-2 pl-6 overflow-hidden">
                            <Search className="w-6 h-6 text-gray-400" />
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="What's your story about?"
                                className="flex-1 bg-transparent border-none text-2xl font-bold focus:ring-0 placeholder:text-gray-700 py-4"
                                onKeyDown={(e) => e.key === 'Enter' && handleSearchIdeas()}
                            />
                            <button
                                onClick={handleSearchIdeas}
                                disabled={isSearching}
                                className="bg-white text-black hover:bg-purple-600 hover:text-white transition-all duration-300 px-10 py-5 rounded-xl font-black uppercase text-xs tracking-[0.2em] disabled:opacity-50"
                            >
                                {isSearching ? <Loader className="w-5 h-5 animate-spin" /> : "Invent"}
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Ideas Selection */}
            {ideas.length > 0 && !script && (
                <section className="max-w-6xl mx-auto px-4 space-y-12 animate-fade-in">
                    <div className="flex items-end justify-between border-b border-white/10 pb-6">
                        <h2 className="text-4xl font-black uppercase italic tracking-tighter font-syne">
                            Potential <span className="text-purple-500">Seeds</span>
                        </h2>
                        <p className="text-[10px] text-gray-500 uppercase tracking-[0.4em] font-black">Choose your path</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
                        {ideas.map((idea, idx) => (
                            <div
                                key={idea.id}
                                onClick={() => handleSelectIdea(idea)}
                                className={clsx(
                                    "group relative cursor-pointer overflow-hidden rounded-[2.5rem] border border-white/5 transition-all duration-700 hover:border-purple-500/50",
                                    idx === 0 ? "md:col-span-8 aspect-[16/10]" : "md:col-span-4 aspect-square md:aspect-auto",
                                    "bg-white/[0.02] hover:bg-purple-600/[0.05] backdrop-blur-xl"
                                )}
                            >
                                <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />

                                <div className="relative z-10 p-10 h-full flex flex-col justify-between">
                                    <div className="flex justify-between items-start">
                                        <div className="px-4 py-1.5 bg-white/5 rounded-full text-[10px] font-black uppercase tracking-[0.3em] border border-white/10">
                                            Path 0{idx + 1}
                                        </div>
                                        <ArrowRight className="w-8 h-8 opacity-0 -translate-x-6 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-700 text-purple-500" />
                                    </div>

                                    <div className="space-y-6">
                                        <h3 className={clsx("font-black uppercase italic leading-[0.9] font-syne tracking-tighter group-hover:text-shadow-neon transition-all duration-700", idx === 0 ? "text-5xl md:text-7xl" : "text-3xl")}>
                                            {idea.title}
                                        </h3>
                                        <p className="text-gray-500 text-lg font-medium leading-relaxed group-hover:text-gray-300 transition-colors line-clamp-3">
                                            {idea.description}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Loading State */}
            {isGeneratingScript && (
                <div className="flex flex-col items-center justify-center p-32 space-y-10">
                    <div className="relative">
                        <div className="absolute inset-0 bg-purple-500/20 blur-3xl animate-pulse rounded-full" />
                        <Loader className="w-24 h-24 text-purple-600 animate-spin-slow relative" />
                        <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 text-white animate-pulse" />
                    </div>
                    <div className="text-center space-y-3">
                        <h3 className="text-3xl font-black uppercase italic tracking-tighter font-syne">Architecting Universe</h3>
                        <p className="text-gray-600 font-black uppercase text-[10px] tracking-[0.5em] animate-pulse">Neural connections established</p>
                    </div>
                </div>
            )}

            {/* Script Dashboard */}
            {script && (
                <div className="max-w-[1400px] mx-auto px-6 grid grid-cols-1 xl:grid-cols-12 gap-16 animate-fade-in-up">
                    {/* Controls Sidebar */}
                    <aside className="xl:col-span-3 space-y-12">
                        <div className="sticky top-12 space-y-16">
                            <div className="space-y-6">
                                <h4 className="text-[10px] font-black uppercase tracking-[0.5em] text-purple-500/80">Persona Core</h4>
                                <div className="space-y-3">
                                    {characterProfiles.map((p) => {
                                        const Icon = p.icon;
                                        const active = charConfig.role === p.name;
                                        return (
                                            <button
                                                key={p.key}
                                                onClick={() => setCharConfig({ ...charConfig, role: p.name })}
                                                className={clsx(
                                                    "relative w-full flex items-center gap-5 p-5 rounded-3xl transition-all duration-500 border overflow-hidden group/btn",
                                                    active ? "bg-white border-white scale-[1.05] shadow-[0_20px_50px_rgba(255,255,255,0.1)]" : "bg-black/20 border-white/5 text-gray-500 hover:border-white/20"
                                                )}
                                            >
                                                <div className={clsx("p-3 rounded-2xl transition-all duration-500", active ? "bg-black text-white" : "bg-white/5 group-hover/btn:bg-white/10")}>
                                                    <Icon className="w-6 h-6" />
                                                </div>
                                                <span className={clsx("text-sm font-black uppercase italic tracking-tight transition-colors duration-500", active ? "text-black" : "text-gray-500 group-hover:text-gray-300")}>{p.name}</span>
                                                {active && <div className="absolute right-6 w-2 h-2 bg-black rounded-full" />}
                                                <div className="absolute inset-x-0 bottom-0 h-1 bg-gradient-to-r from-purple-600 to-pink-600 translate-y-full active:translate-y-0 transition-transform" />
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="space-y-6">
                                <h4 className="text-[10px] font-black uppercase tracking-[0.5em] text-gray-600">Project Integrity</h4>
                                <div className="p-8 bg-white/5 rounded-[2.5rem] border border-white/5 space-y-8 backdrop-blur-3xl">
                                    <div className="space-y-2">
                                        <p className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Master Title</p>
                                        <p className="text-2xl font-black uppercase italic leading-[0.9] font-syne tracking-tighter">{script.title}</p>
                                    </div>
                                    <button
                                        onClick={handleExportZip}
                                        disabled={isExporting}
                                        className="group/export relative w-full aspect-square bg-white rounded-[2rem] flex flex-col items-center justify-center p-6 transition-all duration-500 hover:bg-purple-600 hover:scale-[1.05] hover:-rotate-3 overflow-hidden shadow-2xl"
                                    >
                                        <div className="relative z-10 flex flex-col items-center space-y-4">
                                            {isExporting ? <Loader className="w-10 h-10 text-black animate-spin" /> : <Download className="w-10 h-10 text-black group-hover/export:text-white transition-colors" />}
                                            <span className="text-[10px] font-black uppercase tracking-[0.3em] text-black group-hover/export:text-white transition-colors">Bundle Project</span>
                                        </div>
                                        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20 opacity-0 group-hover/export:opacity-100 transition-opacity" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </aside>

                    {/* Scene Sequence */}
                    <main className="xl:col-span-9 space-y-24 pb-40">
                        {script.scenes.map((scene, idx) => (
                            <div key={idx} className="group relative grid grid-cols-1 lg:grid-cols-12 gap-12 items-start transition-all duration-1000">
                                {/* Visual Master */}
                                <div className="lg:col-span-6 relative aspect-[3/4] rounded-[3rem] overflow-hidden bg-black/40 border border-white/5 group-hover:border-purple-500/30 transition-all duration-1000 group-hover:scale-[0.98]">
                                    {scene.image_url ? (
                                        <img src={scene.image_url} alt={`Scene ${idx + 1}`} className="w-full h-full object-cover transition-transform duration-[2s] group-hover:scale-110" />
                                    ) : (
                                        <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-center space-y-8">
                                            <div className="p-8 bg-white/5 rounded-full border border-white/5 animate-float">
                                                <ImageIcon className="w-16 h-16 text-gray-200 opacity-20" />
                                            </div>
                                            <div className="space-y-4">
                                                <p className="text-[10px] text-gray-600 font-black uppercase tracking-[0.4em]">Environmental Concept</p>
                                                <p className="text-gray-400 font-medium leading-relaxed italic opacity-50 px-4">{scene.background}</p>
                                            </div>
                                            <button
                                                onClick={() => handleGenerateImage(idx, scene.visual_description)}
                                                disabled={isGeneratingImage[idx]}
                                                className="bg-white text-black px-12 py-5 rounded-2xl text-[10px] font-black uppercase tracking-[0.4em] hover:bg-purple-600 hover:text-white transition-all shadow-2xl hover:scale-110"
                                            >
                                                {isGeneratingImage[idx] ? <Loader className="w-5 h-5 animate-spin mx-auto" /> : "Synthesize Visual"}
                                            </button>
                                        </div>
                                    )}
                                    {isGeneratingImage[idx] && (
                                        <div className="absolute inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center p-12 text-center">
                                            <div className="space-y-4">
                                                <Loader className="w-12 h-12 text-purple-600 animate-spin mx-auto" />
                                                <p className="text-[10px] font-black uppercase tracking-[0.5em] text-white">Rendering Reality</p>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Data Layer */}
                                <div className="lg:col-span-6 flex flex-col justify-center h-full space-y-12">
                                    <div className="flex items-center gap-6 group/idx">
                                        <span className="text-[150px] font-black italic text-outline-neon opacity-[0.03] leading-[0.7] group-hover:opacity-10 transition-opacity duration-1000">0{idx + 1}</span>
                                        <div className="h-0.5 flex-1 bg-gradient-to-r from-purple-500/50 to-transparent" />
                                    </div>

                                    <div className="space-y-10">
                                        {/* Dialogue Box */}
                                        <div className="relative p-10 bg-white/[0.03] rounded-[2.5rem] border border-white/10 backdrop-blur-3xl space-y-8 hover:bg-purple-600/[0.03] transition-colors duration-700">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-2 bg-purple-600/20 rounded-lg">
                                                        <MessageSquare className="w-4 h-4 text-purple-400" />
                                                    </div>
                                                    <span className="text-[10px] font-black uppercase tracking-[0.4em] text-purple-400">Oral Output</span>
                                                </div>

                                                {scene.audio_url ? (
                                                    <button
                                                        onClick={() => (document.getElementById(`audio-${idx}`) as HTMLAudioElement)?.play()}
                                                        className="w-12 h-12 bg-white flex items-center justify-center rounded-2xl text-black hover:scale-110 active:scale-95 transition-all shadow-2xl"
                                                    >
                                                        <Play className="w-5 h-5 fill-current" />
                                                        <audio src={scene.audio_url} className="hidden" id={`audio-${idx}`} />
                                                    </button>
                                                ) : (
                                                    <button
                                                        onClick={() => handleGenerateAudio(idx, scene.dialogue)}
                                                        disabled={isGeneratingAudio[idx]}
                                                        className="text-[10px] font-black uppercase tracking-[0.4em] text-gray-600 hover:text-white transition-colors"
                                                    >
                                                        {isGeneratingAudio[idx] ? <Loader className="w-4 h-4 animate-spin" /> : "Engage Speech"}
                                                    </button>
                                                )}
                                            </div>
                                            <p className="text-3xl font-black italic tracking-tighter leading-[1.1] opacity-90 font-syne group-hover:text-purple-300 transition-colors duration-700">
                                                "{scene.dialogue}"
                                            </p>
                                        </div>

                                        {/* Visual Metadata */}
                                        <div className="px-10 space-y-8">
                                            <div className="space-y-4">
                                                <h5 className="text-[10px] font-black text-gray-700 uppercase tracking-[0.4em]">Visual Algorithm</h5>
                                                <p className="text-lg text-gray-500 leading-relaxed font-medium group-hover:text-gray-400 transition-colors duration-700">{scene.visual_description}</p>
                                            </div>

                                            <div className="flex items-center gap-6 pt-10 border-t border-white/5 opacity-0 -translate-x-12 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-1000">
                                                <button
                                                    onClick={() => handleCopyPrompt(scene.video_prompt, idx)}
                                                    className="flex items-center gap-3 text-[10px] font-black uppercase tracking-[0.4em] text-pink-600 hover:text-pink-500 transition-colors"
                                                >
                                                    {copiedIndex === idx ? <Check className="w-5 h-5" /> : <VideoIcon className="w-5 h-5" />}
                                                    Copy Engine Prompt
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </main>
                </div>
            )}
        </div>
    );
}

