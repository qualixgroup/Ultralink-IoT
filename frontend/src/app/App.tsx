import type { ReactNode } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { LoginPage } from "../features/auth/LoginPage";
import { DashboardPage } from "../features/dashboard/DashboardPage";
import {
  AssetsPage,
  DeviceDetailsPage,
  DevicesPage,
  OrganizationsPage,
  SitesPage,
} from "../features/inventory/InventoryPages";
import { ModulePage } from "../features/modules/ModulePage";
import { WorkflowsPage } from "../features/workflows/WorkflowsPage";
import { isAuthenticated } from "../lib/auth";

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
        <Route path="organizations" element={<OrganizationsPage />} />
        <Route path="sites" element={<SitesPage />} />
        <Route path="assets" element={<AssetsPage />} />
        <Route path="devices" element={<DevicesPage />} />
        <Route path="devices/:deviceId" element={<DeviceDetailsPage />} />
        <Route path="alerts" element={<ModulePage title="Alertas" description="Eventos operacionais e regras de severidade." />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="ai" element={<ModulePage title="IA" description="Analises e copilotos operacionais planejados." />} />
        <Route path="integrations" element={<ModulePage title="Integracoes" description="ThingsBoard, MQTT e APIs internas." />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
