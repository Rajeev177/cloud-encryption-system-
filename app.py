from flask import Flask, request, render_template, send_file, redirect, url_for, session, flash
import os
from encryption import encrypt_file_with_aes_and_rsa, decrypt_file_with_aes_and_rsa

app = Flask(__name__)
app.secret_key = 'supersecretkey123'  # Replace with a secure key in production

UPLOAD_FOLDER = 'uploads'
DECRYPT_FOLDER = 'decrypted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPT_FOLDER, exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            encrypted_data = encrypt_file_with_aes_and_rsa(file.read())
            if encrypted_data:
                path = os.path.join(UPLOAD_FOLDER, file.filename + '.enc')
                with open(path, 'wb') as f:
                    f.write(encrypted_data)
                flash("File uploaded and encrypted successfully!")
                return redirect(url_for('index'))

    files = os.listdir(UPLOAD_FOLDER)
    file_sizes = {}
    total_size = 0
    last_file = None

    for file in files:
        filepath = os.path.join(UPLOAD_FOLDER, file)
        size_kb = round(os.path.getsize(filepath) / 1024, 2)
        file_sizes[file] = size_kb
        total_size += size_kb

    if files:
        last_file = max(files, key=lambda f: os.path.getctime(os.path.join(UPLOAD_FOLDER, f)))

    summary = {
        "total_files": len(files),
        "total_size": round(total_size, 2),
        "last_file": last_file or "N/A"
    }

    return render_template('index.html', files=files, file_sizes=file_sizes, summary=summary)

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = decrypt_file_with_aes_and_rsa(encrypted_data)
    decrypted_path = os.path.join(DECRYPT_FOLDER, filename.replace('.enc', ''))
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted_data)
    return send_file(decrypted_path, as_attachment=True)

@app.route('/preview/<filename>')
def preview(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = decrypt_file_with_aes_and_rsa(encrypted_data)
    if decrypted_data:
        try:
            return f"<pre>{decrypted_data.decode('utf-8')}</pre>"
        except:
            return "<h3>❌ Cannot display: Not a text file.</h3>"
    return "<h3>❌ Decryption failed.</h3>"

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)
        flash(f"File '{filename}' deleted successfully.")
        return redirect(url_for('index'))
    except Exception as e:
        return f"<h3>❌ Error deleting file: {e}</h3>"

if __name__ == '__main__':
    app.run(debug=True)
