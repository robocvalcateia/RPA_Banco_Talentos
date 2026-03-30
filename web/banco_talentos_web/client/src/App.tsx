import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import CandidateDetail from "./pages/CandidateDetail";
import { AuthProvider } from "./contexts/AuthContext";
import Login from "./pages/Login";
import PrivateRoute from "./components/PrivateRoute";
function Router() {
  return (
    <Switch>
      <Route path={"/login"} component={Login} />
      <Route path={"/candidato/:id"} component={CandidateDetail} />
      <Route path={"/"} component={() => <PrivateRoute component={Home} />} />
      {/* suas outras rotas */}
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ThemeProvider defaultTheme="light">
          <TooltipProvider>
            <Toaster />
            <Router />
          </TooltipProvider>
        </ThemeProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}


export default App;
