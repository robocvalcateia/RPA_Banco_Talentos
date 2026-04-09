import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Lock, Mail } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "wouter";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const [, setLocation] = useLocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Validação básica
      if (!email || !password) {
        setError("Por favor, preencha todos os campos");
        setLoading(false);
        return;
      }

      if (!email.includes("@")) {
        setError("Por favor, insira um e-mail válido");
        setLoading(false);
        return;
      }

      console.log("📝 Tentando fazer login com:", email);

      // Chamar API de login
      const API_URL = import.meta.env.VITE_API_URL
      const response = await fetch(`${API_URL}/api/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      console.log("📡 Resposta da API:", response.status);

      const data = await response.json();

      console.log("📦 Dados recebidos:", data);

      if (data.success && data.token) {
        console.log("✅ Login bem-sucedido!");
        
        // Salvar token no localStorage
        localStorage.setItem("token", data.token);
        console.log("💾 Token salvo no localStorage");
        
        // Fazer login no contexto
        login({
          email: data.user.email,
          name: data.user.name,
          token: data.token,
        });
        
        console.log("🔐 Usuário autenticado no contexto");
        
        // Redirecionar para Home
        setLocation("/");
        console.log("🚀 Redirecionando para Home");
      } else {
        setError(data.error || "Erro ao fazer login");
        console.error("❌ Erro:", data.error);
      }
    } catch (err) {
      const errorMessage = "Erro ao conectar com o servidor. Verifique se a API está rodando em http://localhost:5000";
      setError(errorMessage);
      console.error("❌ Erro na requisição:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Título */}
        <div className="text-center mb-8">
          <img
            src="/logo_alcateia.jpg"
            alt="JCBuso Tecnologia"
            className="mx-auto mb-6 w-72 rounded-2xl shadow-md"
          />

          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-lg mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>

          <h1 className="text-3xl font-bold text-slate-900">
            Banco de Talentos
          </h1>
          <p className="text-slate-600 mt-2">
            Faça login para acessar
          </p>
        </div>
        {/* Card de Login */}
        <Card className="p-8 shadow-lg border-0">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Campo E-mail */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2">
                E-mail
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                <Input
                  id="email"
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 h-10 border-slate-300"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Campo Senha */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-2">
                Senha
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-10 h-10 border-slate-300"
                  disabled={loading}
                />
              </div>
            </div>

            {/* Mensagem de Erro */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Botão de Login */}
            <Button
              type="submit"
              className="w-full h-10 bg-blue-600 hover:bg-blue-700 text-white font-medium"
              disabled={loading}
            >
              {loading ? "Entrando..." : "Entrar"}
            </Button>

            {/* Informações de Teste */}
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <p className="text-xs text-slate-600 text-center">
                Acesso restrito a usuários autorizados.
                Em caso de dúvidas, contate o administrador do sistema.
              </p>
            </div>
          </form>
        </Card>

        {/* Rodapé */}
        <div className="text-center mt-6">
          <p className="text-sm text-slate-600">
            Sistema de Gerenciamento de Talentos
          </p>
          <p className="text-xs text-slate-500 mt-1">
            © 2026 JCBuso Tecnologia
          </p>
        </div>
      </div>
    </div>
  );
}