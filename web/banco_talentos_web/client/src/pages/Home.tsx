import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, Mail, Phone, MapPin, Briefcase, GraduationCap, FileText, LogOut } from "lucide-react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useLocation } from "wouter";

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

export default function Home() {
  const { user, logout } = useAuth();
  const [, setLocation] = useLocation();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [filteredCandidates, setFilteredCandidates] = useState<Candidate[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<"nome" | "skill" | "endereco">("nome");
  const [loading, setLoading] = useState(true);
  const [processingEmails, setProcessingEmails] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);
  const [error, setError] = useState("");
  const [stats, setStats] = useState({
    total: 0,
    email: 0,
    whatsapp: 0,
  });

  const handleLogout = () => {
    logout();
    setLocation("/login");
  };

  // Buscar candidatos da API
  useEffect(() => {
    const fetchCandidatos = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");

        console.log("🔑 Token do localStorage:", token ? "Existe" : "Não existe");

        if (!token) {
          console.log("⚠️ Sem token, redirecionando para login");
          setLocation("/login");
          return;
        }

        console.log("📡 Buscando candidatos com token...");
        const API_URL = import.meta.env.VITE_API_URL;
        const response = await fetch(`${API_URL}/api/candidatos`, {
          method: 'GET',
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          }
        });

        console.log("📊 Status da resposta:", response.status);

        if (response.status === 401) {
          console.log("❌ Token expirado ou inválido, redirecionando para login");
          localStorage.removeItem("token");
          setLocation("/login");
          return;
        }

        const data = await response.json();
        
        console.log("📦 Dados recebidos:", data);

        if (data.success) {
          console.log("✅ Candidatos carregados:", data.data.length);
          setCandidates(data.data);
          setFilteredCandidates(data.data);

          setStats({
            total: data.data.length,
            email: data.data.filter((c: Candidate) => c.fonte === "email").length,
            whatsapp: data.data.filter((c: Candidate) => c.fonte === "whatsapp").length,
          });
        } else {
          console.error('❌ Erro:', data.error);
          setError(data.error || "Erro ao carregar candidatos");
        }
      } catch (error) {
        console.error('❌ Erro ao buscar candidatos:', error);
        setError("Erro ao conectar com o servidor");
      } finally {
        setLoading(false);
      }
    };

    fetchCandidatos();
  }, [setLocation]);

  // Filtrar candidatos baseado na busca
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredCandidates(candidates);
      return;
    }

    const term = searchTerm.toLowerCase();
    const filtered = candidates.filter(candidate => {
      if (filterType === "nome") {
        return candidate.nome?.toLowerCase().includes(term);
      }

      if (filterType === "skill") {
        return candidate.skills?.toLowerCase().includes(term);
      }

      if (filterType === "endereco") {
        return candidate.endereco?.toLowerCase().includes(term);
      }

      return false;
    });

    setFilteredCandidates(filtered);
  }, [searchTerm, filterType, candidates]);

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("pt-BR");
  };

  const getSourceBadgeColor = (source: string) => {
    return source === "email"
      ? "bg-blue-100 text-blue-800"
      : "bg-blue-50 text-blue-700";
  };

  const getSourceLabel = (source: string) => {
    return source === "email" ? "📧 E-mail" : "💬 WhatsApp";
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-slate-600">Carregando candidatos...</p>
        </div>
      </div>
    );
  }


const handleProcessarEmails = async () => {
  try {
    setProcessingEmails(true);

    const token = localStorage.getItem("token");
    const API_URL = import.meta.env.VITE_API_URL;

    const response = await fetch(`${API_URL}/api/processar-emails`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    });

    const data = await response.json();

    if (data.success) {
      alert("Leitura de e-mails iniciada com sucesso.");
    } else {
      alert(data.error || "Erro ao iniciar processamento.");
    }

  } catch (error) {
    alert("Erro ao conectar com o servidor.");
  } finally {
    setProcessingEmails(false);
  }
};

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur-md border-b border-[#d9f7ef] sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h1 className="text-3xl font-bold text-slate-900">Banco de Talentos</h1>
              <p className="text-slate-600 mt-1">Consulte e gerencie candidatos</p>
            </div>
            <div className="flex items-center gap-4 ml-10">
              <Card className="w-[150px] p-4 bg-slate-50 border-slate-200">
                <div className="text-sm text-slate-600">Total de Candidatos</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">{stats.total}</div>
              </Card>

            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className="text-sm text-slate-600">Logado como</div>
                <div className="text-sm font-medium text-slate-900">{user?.name}</div>
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="border-[#08B79B] text-[#08B79B] hover:bg-[#08B79B] hover:text-white shadow-sm"
              >
                <LogOut className="w-4 h-4" />
                Sair
              </Button>
            </div>
          </div>
          <div className="mt-1 mb-2">
          <Button
            onClick={handleProcessarEmails}
            disabled={processingEmails}
            variant="outline"
            size="sm"
            className="border-[#08B79B] text-[#08B79B] hover:bg-[#08B79B] hover:text-white shadow-sm"
          >
            {processingEmails ? "Processando..." : "Processar Leitura de E-mails"}
          </Button>
          </div>


          {/* Busca */}
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
              <Input
                placeholder={`Buscar por ${filterType === "nome"? "nome": filterType === "skill"? "skill": "endereço"}...`}
                value={searchTerm}
                onChange={handleSearch}
                className="pl-10 h-10 border-slate-300"
              />
            </div>
            <Button
              onClick={() =>setFilterType(filterType === "nome"? "skill": filterType === "skill"? "endereco": "nome")}
              variant="outline"
              size="sm"
              className="min-w-max border-[#08B79B] text-[#08B79B] hover:bg-[#08B79B] hover:text-white"
            >
              {filterType === "nome"? "Buscar por Skill": filterType === "skill"? "Buscar por Endereço": "Buscar por Nome"}
            </Button>
          </div>
        </div>
      </header>

      {/* Conteúdo */}
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {filteredCandidates.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600 text-lg">Nenhum candidato encontrado</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {filteredCandidates.map((candidate) => (
              <Card
                key={candidate._id}
                className="p-6 border border-[#d9f7ef] hover:border-[#08B79B] hover:shadow-xl transition-all duration-300 cursor-pointer rounded-2xl bg-white"
                onClick={() => setLocation(`/candidato/${candidate._id}`)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">{candidate.nome}</h3>
                    <Badge className={getSourceBadgeColor(candidate.fonte)}>
                      {getSourceLabel(candidate.fonte)}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-2 text-sm text-slate-600">
                  {candidate.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      <span>{candidate.email}</span>
                    </div>
                  )}
                  {candidate.telefone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      <span>{candidate.telefone}</span>
                    </div>
                  )}
                  {candidate.endereco && (
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>{candidate.endereco}</span>
                    </div>
                  )}
                </div>

                {candidate.skills && (
                  <div className="mt-4">
                    <p className="text-xs font-medium text-slate-700 mb-2">Skills</p>
                    <div className="mt-2 text-sm text-slate-600 leading-relaxed">
                      {candidate.skills && (
                        <p className="text-sm text-slate-600 leading-relaxed">
                          {candidate.skills}
                        </p>
                      )}

                      {candidate.skills?.split(/,|\n|\|/).length > 5 && (
                        <span className="text-xs text-slate-500">
                          +{candidate.skills.split(/,|\n|\|/).length - 5}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-4 pt-4 border-t border-slate-200 text-xs text-slate-500">
                  Atualizado: {formatDate(candidate.data_atualizacao)}
                </div>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Modal de Detalhes */}
      {selectedCandidate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="w-full max-w-2xl max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-slate-900">{selectedCandidate.nome}</h2>
                  <Badge className={getSourceBadgeColor(selectedCandidate.fonte)}>
                    {getSourceLabel(selectedCandidate.fonte)}
                  </Badge>
                </div>
                <Button
                  onClick={() => setSelectedCandidate(null)}
                  variant="ghost"
                  size="sm"
                >
                  ✕
                </Button>
              </div>

              <div className="space-y-4">
                {selectedCandidate.email && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">E-mail</p>
                    <p className="text-slate-600">{selectedCandidate.email}</p>
                  </div>
                )}
                {selectedCandidate.telefone && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Telefone</p>
                    <p className="text-slate-600">{selectedCandidate.telefone}</p>
                  </div>
                )}
                {selectedCandidate.endereco && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Endereço</p>
                    <p className="text-slate-600">{selectedCandidate.endereco}</p>
                  </div>
                )}
                {selectedCandidate.skills && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Skills</p>
                    <p className="text-slate-600">{selectedCandidate.skills}</p>
                  </div>
                )}
                {selectedCandidate.formacao_academica && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Formação Acadêmica</p>
                    <p className="text-slate-600">{selectedCandidate.formacao_academica}</p>
                  </div>
                )}
                {selectedCandidate.experiencia_profissional && (
                  <div>
                    <p className="text-sm font-medium text-slate-700">Experiência Profissional</p>
                    <p className="text-slate-600">{selectedCandidate.experiencia_profissional}</p>
                  </div>
                )}
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}