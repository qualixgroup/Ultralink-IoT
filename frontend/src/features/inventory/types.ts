export type Partner = {
  id: string;
  name: string;
  status: string;
  created_at: string;
};

export type Organization = {
  id: string;
  partner_id: string;
  name: string;
  document: string | null;
  status: string;
  created_at: string;
};

export type Site = {
  id: string;
  organization_id: string;
  name: string;
  address: string | null;
  status: string;
  created_at: string;
};

export type Asset = {
  id: string;
  organization_id: string;
  site_id: string;
  name: string;
  type: string;
  status: string;
  created_at: string;
};

export type Device = {
  id: string;
  organization_id: string;
  site_id: string;
  asset_id: string;
  name: string;
  label: string | null;
  type: string;
  status: string;
  attributes: Record<string, unknown>;
  created_at: string;
};

export type DeviceTelemetry = {
  device_id: string;
  temperatura: number;
  bateria: number;
  combustivel: number;
  rssi: number;
  ultima_atualizacao: string;
  source: string;
};
