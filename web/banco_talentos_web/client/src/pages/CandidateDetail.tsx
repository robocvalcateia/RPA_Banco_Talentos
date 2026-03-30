import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, ArrowLeft, Edit2, Save, X } from "lucide-react";
import { useLocation, useRoute } from "wouter";
import { useAuth } from "@/contexts/AuthContext";

interface Candidate {
  _id: string;
  nome: string;
  email: string;
  telefone: string;
  endereco: string;
  skills: string;
  formacao_academica: string;
  cursos_certificacoes: string;
  nivel_ingles: string;
  nivel_espanhol: string;
  experiencia_profissional: string;
  linkedin: string;
  fonte: string;
  data_criacao: string;
  data_atualizacao: string;
}

export default function CandidateDetail() {
  const [, params] = useRoute("/candidato/:id");
  const [, setLocation] = useLocation();
  const { user } = useAuth();
  
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  const [formData, setFormData] = useState<Candidate | null>(null);

  // Buscar dados do candidato
  useEffect(() => {
    const fetchCandidate = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");

        if (!token) {
          setLocation("/login");
          return;
        }
        const API_URL = import.meta.env.VITE_API_URL;
        const response = await fetch(`${API_URL}/api/candidatos/${params?.id}`, {
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });

        if (response.status === 401) {
          localStorage.removeItem("token");
          setLocation("/login");
          return;
        }

        const data = await response.json();

        if (data.success) {
          setCandidate(data.data);
          setFormData(data.data);
        } else {
          setError(data.error || "Candidato não encontrado");
        }
      } catch (err) {
        console.error("Erro ao buscar candidato:", err);
        setError("Erro ao carregar candidato");
      } finally {
        setLoading(false);
      }
    };

    if (params?.id) {
      fetchCandidate();
    }
  }, [params?.id, setLocation]);

  const handleInputChange = (field: keyof Candidate, value: string) => {
    if (formData) {
      setFormData({
        ...formData,
        [field]: value
      });
    }
  };

  const handleSave = async () => {
    if (!formData) return;

    try {
      setIsSaving(true);
      const token = localStorage.getItem("token");
      const API_URL = import.meta.env.VITE_API_URL;
      const response = await fetch(`${API_URL}/api/candidatos/${params?.id}`, {
        method: "PUT",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.success) {
        setCandidate(formData);
        setIsEditing(false);
        // Mostrar mensagem de sucesso
        alert("Candidato atualizado com sucesso!");
      } else {
        setError(data.error || "Erro ao atualizar candidato");
      }
    } catch (err) {
      console.error("Erro ao salvar:", err);
      setError("Erro ao salvar candidato");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData(candidate);
    setIsEditing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600">Carregando candidato...</p>
        </div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4">
        <div className="max-w-4xl mx-auto">
          <Button
            onClick={() => setLocation("/")}
            variant="outline"
            className="mb-4 gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </Button>
          <Card className="p-8 text-center">
            <p className="text-red-600 text-lg">{error || "Candidato não encontrado"}</p>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Button
            onClick={() => setLocation("/")}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </Button>
          
          {!isEditing ? (
            <Button
              onClick={() => setIsEditing(true)}
              variant="default"
              size="sm"
              className="gap-2"
            >
              <Edit2 className="w-4 h-4" />
              Editar
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button
                onClick={handleSave}
                disabled={isSaving}
                variant="default"
                size="sm"
                className="gap-2"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Salvando...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    Salvar
                  </>
                )}
              </Button>
              <Button
                onClick={handleCancel}
                disabled={isSaving}
                variant="outline"
                size="sm"
                className="gap-2"
              >
                <X className="w-4 h-4" />
                Cancelar
              </Button>
            </div>
          )}
        </div>
      </header>

      {/* Conteúdo */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <Card className="p-8">
          {/* Título e Badge */}
          <div className="flex items-start justify-between mb-8">
            <div>
              {isEditing ? (
                <Input
                  value={formData?.nome || ""}
                  onChange={(e) => handleInputChange("nome", e.target.value)}
                  className="text-2xl font-bold mb-2"
                />
              ) : (
                <h1 className="text-3xl font-bold text-slate-900 mb-2">{candidate.nome}</h1>
              )}
              <Badge className={candidate.fonte === "email" ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"}>
                {candidate.fonte === "email" ? "📧 E-mail" : "💬 WhatsApp"}
              </Badge>
            </div>
          </div>

          {/* Grid de Campos */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* E-mail */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">E-mail</label>
              {isEditing ? (
                <Input
                  value={formData?.email || ""}
                  onChange={(e) => handleInputChange("email", e.target.value)}
                  type="email"
                />
              ) : (
                <p className="text-slate-600">{candidate.email}</p>
              )}
            </div>

            {/* Telefone */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Telefone</label>
              {isEditing ? (
                <Input
                  value={formData?.telefone || ""}
                  onChange={(e) => handleInputChange("telefone", e.target.value)}
                />
              ) : (
                <p className="text-slate-600">{candidate.telefone}</p>
              )}
            </div>

            {/* Endereço */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Endereço</label>
              {isEditing ? (
                <Input
                  value={formData?.endereco || ""}
                  onChange={(e) => handleInputChange("endereco", e.target.value)}
                />
              ) : (
                <p className="text-slate-600">{candidate.endereco}</p>
              )}
            </div>

            {/* LinkedIn */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">LinkedIn</label>
              {isEditing ? (
                <Input
                  value={formData?.linkedin || ""}
                  onChange={(e) => handleInputChange("linkedin", e.target.value)}
                  type="url"
                />
              ) : (
                <p className="text-slate-600">{candidate.linkedin || "-"}</p>
              )}
            </div>

            {/* Nível de Inglês */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Nível de Inglês</label>
              {isEditing ? (
                <Input
                  value={formData?.nivel_ingles || ""}
                  onChange={(e) => handleInputChange("nivel_ingles", e.target.value)}
                />
              ) : (
                <p className="text-slate-600">{candidate.nivel_ingles || "-"}</p>
              )}
            </div>

            {/* Nível de Espanhol */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Nível de Espanhol</label>
              {isEditing ? (
                <Input
                  value={formData?.nivel_espanhol || ""}
                  onChange={(e) => handleInputChange("nivel_espanhol", e.target.value)}
                />
              ) : (
                <p className="text-slate-600">{candidate.nivel_espanhol || "-"}</p>
              )}
            </div>
          </div>

          {/* Campos de Texto Longo */}
          <div className="mt-8 space-y-6">
            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Skills</label>
              {isEditing ? (
                <textarea
                  value={formData?.skills || ""}
                  onChange={(e) => handleInputChange("skills", e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md"
                  rows={3}
                />
              ) : (
                <p className="text-slate-600 whitespace-pre-wrap">{candidate.skills}</p>
              )}
            </div>

            {/* Formação Acadêmica */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Formação Acadêmica</label>
              {isEditing ? (
                <textarea
                  value={formData?.formacao_academica || ""}
                  onChange={(e) => handleInputChange("formacao_academica", e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md"
                  rows={3}
                />
              ) : (
                <p className="text-slate-600 whitespace-pre-wrap">{candidate.formacao_academica}</p>
              )}
            </div>

            {/* Cursos e Certificações */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Cursos e Certificações</label>
              {isEditing ? (
                <textarea
                  value={formData?.cursos_certificacoes || ""}
                  onChange={(e) => handleInputChange("cursos_certificacoes", e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md"
                  rows={3}
                />
              ) : (
                <p className="text-slate-600 whitespace-pre-wrap">{candidate.cursos_certificacoes}</p>
              )}
            </div>

            {/* Experiência Profissional */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">Experiência Profissional</label>
              {isEditing ? (
                <textarea
                  value={formData?.experiencia_profissional || ""}
                  onChange={(e) => handleInputChange("experiencia_profissional", e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-md"
                  rows={4}
                />
              ) : (
                <p className="text-slate-600 whitespace-pre-wrap">{candidate.experiencia_profissional}</p>
              )}
            </div>
          </div>

          {/* Rodapé com Datas */}
          <div className="mt-8 pt-6 border-t border-slate-200 text-sm text-slate-500">
            <p>Criado em: {new Date(candidate.data_criacao).toLocaleDateString("pt-BR")}</p>
            <p>Atualizado em: {new Date(candidate.data_atualizacao).toLocaleDateString("pt-BR")}</p>
          </div>
        </Card>
      </main>
    </div>
  );
}