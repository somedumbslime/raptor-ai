import { useState, useRef } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [resultUrl, setResultUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const progressRef = useRef();

  // Анимация прогресса (фейковая, для UX)
  const startProgress = () => {
    setProgress(0);
    progressRef.current = setInterval(() => {
      setProgress((old) => {
        if (old < 95) return old + Math.random() * 3;
        return old;
      });
    }, 100);
  };

  const stopProgress = () => {
    clearInterval(progressRef.current);
    setProgress(100);
    setTimeout(() => setProgress(0), 800);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (!droppedFile) return;
    setFile(droppedFile);
    await uploadFile(droppedFile);
  };

  const uploadFile = async (selectedFile) => {
    const formData = new FormData();
    formData.append("file", selectedFile);

    setLoading(true);
    startProgress();
    const res = await fetch("http://localhost:8000/predict/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResultUrl(`http://localhost:8000/${data.output_path}`);
    setLoading(false);
    stopProgress();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white p-6 flex flex-col items-center">
      <h1 className="text-4xl font-extrabold mb-6 tracking-tight drop-shadow-lg">
        ReconAI — демо-модель
      </h1>

      <div
        className={`w-full max-w-xl h-64 border-4 border-dashed rounded-2xl flex items-center justify-center text-center cursor-pointer transition-all duration-300 shadow-xl ${loading
          ? "border-green-400 bg-gray-800/60"
          : "border-blue-400 hover:border-green-400 bg-gray-800/40"
          }`}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        {loading ? (
          <div className="w-full">
            <p className="text-lg mb-4">Загрузка и обработка...</p>
            <div className="w-3/4 mx-auto h-4 bg-gray-700 rounded-full overflow-hidden shadow-inner">
              <div
                className="h-full bg-green-400 transition-all duration-200"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        ) : (
          <p className="text-lg opacity-80">
            Перетащи <span className="font-bold text-blue-300">видео</span> или{" "}
            <span className="font-bold text-green-300">фото</span> сюда
          </p>
        )}
      </div>

      {resultUrl && (
        <div className="mt-10 w-full max-w-xl bg-gray-800 rounded-xl shadow-2xl p-6">
          <h2 className="text-xl mb-4 font-semibold text-green-300">Результат:</h2>
          {file?.type.includes("image") ? (
            <img
              src={resultUrl}
              alt="Result"
              className="max-w-xl rounded shadow-lg mx-auto"
            />
          ) : (
            <video controls className="max-w-xl rounded shadow-lg mx-auto">
              <source src={resultUrl} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
        </div>
      )}

      <div className="bg-red-500 text-3xl p-10 text-white">TAILWIND TEST</div>
    </div>
  );
}

export default App;
