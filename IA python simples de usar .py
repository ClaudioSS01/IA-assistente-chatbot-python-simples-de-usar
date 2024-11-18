import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import os
from groq import Groq

class ChatbotGroq:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot com Groq")
        self.root.geometry("500x500")

        # Área de exibição do chat
        self.chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Campo de entrada de texto
        self.entry = tk.Entry(root)
        self.entry.pack(padx=10, pady=5, fill=tk.X)
        self.entry.bind("<Return>", self.enviar_comando)

        # Botão para enviar a mensagem
        self.send_button = tk.Button(root, text="Enviar", command=self.enviar_comando)
        self.send_button.pack(padx=10, pady=10)

        # Gerenciar a chave da API
        self.api_key = self.carregar_ou_solicitar_chave()
        self.client = Groq(api_key=self.api_key)

    def carregar_ou_solicitar_chave(self):
        """Carrega a chave da API do arquivo .env ou solicita ao usuário."""
        chave_env_path = ".env"

        # Lê do arquivo .env se existir
        if os.path.exists(chave_env_path):
            with open(chave_env_path, "r") as file:
                for line in file:
                    if line.startswith("GROQ_API_KEY="):
                        return line.strip().split("=", 1)[1]

        # Solicita ao usuário
        chave = simpledialog.askstring("Chave de API", "Insira sua chave de API do Groq acesse https://console.groq.com/keys:")
        if not chave:
            messagebox.showerror("Erro", "Chave de API é necessária para o funcionamento. acesse https://console.groq.com/keys para pegar sua chave de api")
            self.root.quit()

        # Salva no arquivo .env
        with open(chave_env_path, "w") as file:
            file.write(f"GROQ_API_KEY={chave}\n")
        return chave

    def atualizar_chat(self, sender, message):
        """Adiciona mensagens ao chat."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def enviar_comando(self, event=None):
        """Envia o comando para o Groq e exibe a resposta."""
        comando = self.entry.get().strip()
        if not comando:
            messagebox.showwarning("Aviso", "Digite um comando antes de enviar.")
            return

        # Adiciona mensagem do usuário no chat
        self.atualizar_chat("Usuário", comando)
        self.entry.delete(0, tk.END)

        # Adiciona mensagem de status
        self.atualizar_chat("Assistente", "Processando...")

        # Chamada real à API do Groq
        try:
            resposta = self.enviar_para_groq(comando)
            self.atualizar_chat("Groq", resposta)
        except Exception as e:
            self.atualizar_chat("Erro", f"Falha ao se comunicar com o Groq: {e}")

    def enviar_para_groq(self, comando):
        """Envia um comando para a API do Groq e retorna a resposta."""
        try:
            completion = self.client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "user", "content": comando}
                ],
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            resposta = completion.choices[0].message.content
            return resposta
        except Exception as e:
            raise Exception(f"Erro ao processar o comando: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotGroq(root)
    root.mainloop()
