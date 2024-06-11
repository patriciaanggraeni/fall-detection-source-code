import os
import subprocess


def run_script(script_path):
    return subprocess.Popen(["python", script_path])


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "../assets/credential_key/key.json"

    # Menggunakan os.path.join untuk membangun path dengan benar
    base_dir = os.path.dirname(os.path.abspath(__file__))
    publisher_path = os.path.join(base_dir, "mqtt", "publisher.py")
    subscriber_path = os.path.join(base_dir, "mqtt", "subcriber.py")

    # Pastikan file ada di lokasi yang benar
    if not os.path.exists(publisher_path):
        print(f"File not found: {publisher_path}")
    if not os.path.exists(subscriber_path):
        print(f"File not found: {subscriber_path}")
        print("Path to subscriber.py:", subscriber_path)

    # Jalankan publisher dan subscriber jika file ditemukan
    if os.path.exists(publisher_path) and os.path.exists(subscriber_path):
        publisher_process = run_script(publisher_path)
        subscriber_process = run_script(subscriber_path)

        try:
            # Tunggu proses untuk menyelesaikan
            publisher_process.wait()
            subscriber_process.wait()
        except KeyboardInterrupt:
            # Handle keyboard interrupt (Ctrl+C) untuk menghentikan proses
            print("KeyboardInterrupt received, terminating processes...")
            publisher_process.terminate()
            subscriber_process.terminate()
