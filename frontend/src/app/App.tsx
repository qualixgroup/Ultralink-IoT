import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { isAuthenticated } from "../lib/auth";
import { LoginPage } from "../features/auth/LoginPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import { ModulePage } from "../features/modules/ModulePage";
import { WorkflowsPage } from "../features/workflows/WorkflowsPage";

function ProtectedRoute({ children }: { children: ReactNode }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="devices" element={<ModulePage title="Dispositivos" description="Inventário sincronizado com ThingsBoard." />} />
        <Route path="alerts" element={<ModulePage title="Alertas" description="Eventos operacionais e regras de severidade." />} />
        <Route path="companies" element={<ModulePage title="Empresas" description="Gestão multiempresa para operação SaaS." />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="ai" element={<ModulePage title="IA" description="Análises e copilotos operacionais planejados." />} />
        <Route path="integrations" element={<ModulePage title="Integrações" description="ThingsBoard, MQTT, WhatsApp e OpenAI." />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
