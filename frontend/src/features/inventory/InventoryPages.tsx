import { useMemo, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BatteryCharging,
  Building2,
  Factory,
  Fuel,
  MapPin,
  Plus,
  RadioTower,
  Signal,
  Thermometer,
  type LucideIcon,
} from "lucide-react";

import { StatusPill } from "../../components/ui/StatusPill";
import { apiRequest } from "../../lib/api";
import type { Asset, Device, DeviceTelemetry, Organization, Partner, Site } from "./types";

type Tone = "success" | "warning" | "danger" | "neutral";

function statusTone(status: string): Tone {
  if (["active", "online", "ok"].includes(status)) {
    return "success";
  }
  if (["deleted", "offline", "error"].includes(status)) {
    return "danger";
  }
  if (["provisioning", "sync_failed"].includes(status)) {
    return "warning";
  }
  return "neutral";
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return "-";
  }
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function PageHeader({ title, eyebrow }: { title: string; eyebrow: string }) {
  return (
    <section className="flex flex-wrap items-center justify-between gap-3">
      <div>
        <p className="text-sm text-slate-500">{eyebrow}</p>
        <h2 className="text-2xl font-semibold tracking-normal text-white">{title}</h2>
      </div>
      <StatusPill tone="success">API</StatusPill>
    </section>
  );
}

function Panel({ children }: { children: ReactNode }) {
  return <section className="rounded-lg border border-white/10 bg-panel p-4 shadow-glow">{children}</section>;
}

function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm text-slate-400">{label}</span>
      {children}
    </label>
  );
}

const inputClass =
  "h-11 w-full rounded-lg border border-white/10 bg-black/20 px-3 text-sm text-white outline-none focus:border-cyan-300/50";

function SubmitButton({ label, disabled }: { label: string; disabled?: boolean }) {
  return (
    <button
      type="submit"
      disabled={disabled}
      className="inline-flex h-11 items-center justify-center gap-2 rounded-lg bg-cyan-300 px-4 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-70"
    >
      <Plus className="h-4 w-4" aria-hidden="true" />
      {label}
    </button>
  );
}

function EmptyRow({ colSpan }: { colSpan: number }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-8 text-center text-sm text-slate-500">
        Nenhum registro encontrado.
      </td>
    </tr>
  );
}

function useInventory() {
  const partners = useQuery({
    queryKey: ["partners"],
    queryFn: () => apiRequest<Partner[]>("/partners"),
  });
  const organizations = useQuery({
    queryKey: ["organizations"],
    queryFn: () => apiRequest<Organization[]>("/organizations"),
  });
  const sites = useQuery({
    queryKey: ["sites"],
    queryFn: () => apiRequest<Site[]>("/sites"),
  });
  const assets = useQuery({
    queryKey: ["assets"],
    queryFn: () => apiRequest<Asset[]>("/assets"),
  });
  const devices = useQuery({
    queryKey: ["devices"],
    queryFn: () => apiRequest<Device[]>("/devices"),
  });

  return { partners, organizations, sites, assets, devices };
}

export function OrganizationsPage() {
  const queryClient = useQueryClient();
  const { partners, organizations } = useInventory();
  const [partnerId, setPartnerId] = useState("");
  const [name, setName] = useState("");
  const [document, setDocument] = useState("");

  const createOrganization = useMutation({
    mutationFn: () =>
      apiRequest<Organization>("/organizations", {
        method: "POST",
        body: JSON.stringify({ partner_id: partnerId, name, document: document || null }),
      }),
    onSuccess: () => {
      setName("");
      setDocument("");
      void queryClient.invalidateQueries({ queryKey: ["organizations"] });
    },
  });

  const partnerById = new Map((partners.data ?? []).map((partner) => [partner.id, partner.name]));

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Inventario" title="Organizations" />
      <Panel>
        <form
          className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_auto]"
          onSubmit={(event: FormEvent<HTMLFormElement>) => {
            event.preventDefault();
            createOrganization.mutate();
          }}
        >
          <Field label="Partner">
            <select className={inputClass} value={partnerId} onChange={(event) => setPartnerId(event.target.value)} required>
              <option value="">Selecione</option>
              {(partners.data ?? []).map((partner) => (
                <option key={partner.id} value={partner.id}>
                  {partner.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Nome">
            <input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} required />
          </Field>
          <Field label="Documento">
            <input className={inputClass} value={document} onChange={(event) => setDocument(event.target.value)} />
          </Field>
          <div className="flex items-end">
            <SubmitButton label="Criar" disabled={createOrganization.isPending} />
          </div>
        </form>
      </Panel>

      <Panel>
        <Table headers={["Nome", "Partner", "Documento", "Status", "Criado em"]}>
          {(organizations.data ?? []).length ? (
            (organizations.data ?? []).map((organization) => (
              <tr key={organization.id} className="border-t border-white/10">
                <td className="px-4 py-3 text-sm text-white">{organization.name}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{partnerById.get(organization.partner_id) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{organization.document ?? "-"}</td>
                <td className="px-4 py-3">
                  <StatusPill tone={statusTone(organization.status)}>{organization.status}</StatusPill>
                </td>
                <td className="px-4 py-3 text-sm text-slate-400">{formatDate(organization.created_at)}</td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={5} />
          )}
        </Table>
      </Panel>
    </div>
  );
}

export function SitesPage() {
  const queryClient = useQueryClient();
  const { organizations, sites } = useInventory();
  const [organizationId, setOrganizationId] = useState("");
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");

  const createSite = useMutation({
    mutationFn: () =>
      apiRequest<Site>("/sites", {
        method: "POST",
        body: JSON.stringify({ organization_id: organizationId, name, address: address || null }),
      }),
    onSuccess: () => {
      setName("");
      setAddress("");
      void queryClient.invalidateQueries({ queryKey: ["sites"] });
    },
  });

  const organizationById = new Map((organizations.data ?? []).map((organization) => [organization.id, organization.name]));

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Inventario" title="Sites" />
      <Panel>
        <form
          className="grid gap-3 md:grid-cols-[1fr_1fr_1fr_auto]"
          onSubmit={(event) => {
            event.preventDefault();
            createSite.mutate();
          }}
        >
          <Field label="Organization">
            <select
              className={inputClass}
              value={organizationId}
              onChange={(event) => setOrganizationId(event.target.value)}
              required
            >
              <option value="">Selecione</option>
              {(organizations.data ?? []).map((organization) => (
                <option key={organization.id} value={organization.id}>
                  {organization.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Nome">
            <input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} required />
          </Field>
          <Field label="Endereco">
            <input className={inputClass} value={address} onChange={(event) => setAddress(event.target.value)} />
          </Field>
          <div className="flex items-end">
            <SubmitButton label="Criar" disabled={createSite.isPending} />
          </div>
        </form>
      </Panel>

      <Panel>
        <Table headers={["Nome", "Organization", "Endereco", "Status", "Criado em"]}>
          {(sites.data ?? []).length ? (
            (sites.data ?? []).map((site) => (
              <tr key={site.id} className="border-t border-white/10">
                <td className="px-4 py-3 text-sm text-white">{site.name}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{organizationById.get(site.organization_id) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{site.address ?? "-"}</td>
                <td className="px-4 py-3">
                  <StatusPill tone={statusTone(site.status)}>{site.status}</StatusPill>
                </td>
                <td className="px-4 py-3 text-sm text-slate-400">{formatDate(site.created_at)}</td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={5} />
          )}
        </Table>
      </Panel>
    </div>
  );
}

export function AssetsPage() {
  const queryClient = useQueryClient();
  const { organizations, sites, assets } = useInventory();
  const [organizationId, setOrganizationId] = useState("");
  const [siteId, setSiteId] = useState("");
  const [name, setName] = useState("");
  const [type, setType] = useState("generic");

  const availableSites = (sites.data ?? []).filter((site) => !organizationId || site.organization_id === organizationId);
  const createAsset = useMutation({
    mutationFn: () =>
      apiRequest<Asset>("/assets", {
        method: "POST",
        body: JSON.stringify({ organization_id: organizationId, site_id: siteId, name, type }),
      }),
    onSuccess: () => {
      setName("");
      void queryClient.invalidateQueries({ queryKey: ["assets"] });
    },
  });

  const siteById = new Map((sites.data ?? []).map((site) => [site.id, site.name]));
  const organizationById = new Map((organizations.data ?? []).map((organization) => [organization.id, organization.name]));

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Inventario" title="Assets" />
      <Panel>
        <form
          className="grid gap-3 lg:grid-cols-[1fr_1fr_1fr_1fr_auto]"
          onSubmit={(event) => {
            event.preventDefault();
            createAsset.mutate();
          }}
        >
          <Field label="Organization">
            <select
              className={inputClass}
              value={organizationId}
              onChange={(event) => {
                setOrganizationId(event.target.value);
                setSiteId("");
              }}
              required
            >
              <option value="">Selecione</option>
              {(organizations.data ?? []).map((organization) => (
                <option key={organization.id} value={organization.id}>
                  {organization.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Site">
            <select className={inputClass} value={siteId} onChange={(event) => setSiteId(event.target.value)} required>
              <option value="">Selecione</option>
              {availableSites.map((site) => (
                <option key={site.id} value={site.id}>
                  {site.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Nome">
            <input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} required />
          </Field>
          <Field label="Tipo">
            <input className={inputClass} value={type} onChange={(event) => setType(event.target.value)} required />
          </Field>
          <div className="flex items-end">
            <SubmitButton label="Criar" disabled={createAsset.isPending} />
          </div>
        </form>
      </Panel>

      <Panel>
        <Table headers={["Nome", "Tipo", "Organization", "Site", "Status"]}>
          {(assets.data ?? []).length ? (
            (assets.data ?? []).map((asset) => (
              <tr key={asset.id} className="border-t border-white/10">
                <td className="px-4 py-3 text-sm text-white">{asset.name}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{asset.type}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{organizationById.get(asset.organization_id) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-400">{siteById.get(asset.site_id) ?? "-"}</td>
                <td className="px-4 py-3">
                  <StatusPill tone={statusTone(asset.status)}>{asset.status}</StatusPill>
                </td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={5} />
          )}
        </Table>
      </Panel>
    </div>
  );
}

export function DevicesPage() {
  const queryClient = useQueryClient();
  const { organizations, sites, assets, devices } = useInventory();
  const [organizationId, setOrganizationId] = useState("");
  const [assetId, setAssetId] = useState("");
  const [name, setName] = useState("");
  const [type, setType] = useState("sensor");

  const availableAssets = (assets.data ?? []).filter((asset) => !organizationId || asset.organization_id === organizationId);
  const createDevice = useMutation({
    mutationFn: () =>
      apiRequest<Device>("/devices", {
        method: "POST",
        body: JSON.stringify({ organization_id: organizationId, asset_id: assetId, name, type }),
      }),
    onSuccess: () => {
      setName("");
      void queryClient.invalidateQueries({ queryKey: ["devices"] });
    },
  });

  const organizationById = new Map((organizations.data ?? []).map((organization) => [organization.id, organization.name]));
  const siteById = new Map((sites.data ?? []).map((site) => [site.id, site.name]));
  const assetById = new Map((assets.data ?? []).map((asset) => [asset.id, asset]));

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Operacao" title="Devices" />
      <Panel>
        <form
          className="grid gap-3 lg:grid-cols-[1fr_1fr_1fr_1fr_auto]"
          onSubmit={(event) => {
            event.preventDefault();
            createDevice.mutate();
          }}
        >
          <Field label="Organization">
            <select
              className={inputClass}
              value={organizationId}
              onChange={(event) => {
                setOrganizationId(event.target.value);
                setAssetId("");
              }}
              required
            >
              <option value="">Selecione</option>
              {(organizations.data ?? []).map((organization) => (
                <option key={organization.id} value={organization.id}>
                  {organization.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Asset">
            <select className={inputClass} value={assetId} onChange={(event) => setAssetId(event.target.value)} required>
              <option value="">Selecione</option>
              {availableAssets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Nome">
            <input className={inputClass} value={name} onChange={(event) => setName(event.target.value)} required />
          </Field>
          <Field label="Tipo">
            <input className={inputClass} value={type} onChange={(event) => setType(event.target.value)} required />
          </Field>
          <div className="flex items-end">
            <SubmitButton label="Cadastrar" disabled={createDevice.isPending} />
          </div>
        </form>
      </Panel>

      <Panel>
        <Table headers={["Nome", "Status", "Organization", "Site", "Asset", "Detalhes"]}>
          {(devices.data ?? []).length ? (
            (devices.data ?? []).map((device) => {
              const asset = assetById.get(device.asset_id);
              return (
                <tr key={device.id} className="border-t border-white/10">
                  <td className="px-4 py-3 text-sm text-white">{device.name}</td>
                  <td className="px-4 py-3">
                    <StatusPill tone={statusTone(device.status)}>{device.status}</StatusPill>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-400">{organizationById.get(device.organization_id) ?? "-"}</td>
                  <td className="px-4 py-3 text-sm text-slate-400">{siteById.get(device.site_id) ?? "-"}</td>
                  <td className="px-4 py-3 text-sm text-slate-400">{asset?.name ?? "-"}</td>
                  <td className="px-4 py-3">
                    <Link className="text-sm font-medium text-cyan-200 hover:text-cyan-100" to={`/devices/${device.id}`}>
                      Abrir
                    </Link>
                  </td>
                </tr>
              );
            })
          ) : (
            <EmptyRow colSpan={6} />
          )}
        </Table>
      </Panel>
    </div>
  );
}

export function DeviceDetailsPage() {
  const { deviceId } = useParams<{ deviceId: string }>();
  const { organizations, sites, assets } = useInventory();
  const device = useQuery({
    queryKey: ["devices", deviceId],
    enabled: Boolean(deviceId),
    queryFn: () => apiRequest<Device>(`/devices/${deviceId}`),
  });
  const telemetry = useQuery({
    queryKey: ["devices", deviceId, "telemetry"],
    enabled: Boolean(deviceId),
    queryFn: () => apiRequest<DeviceTelemetry>(`/devices/${deviceId}/telemetry`),
    refetchInterval: 30000,
  });

  const organizationById = new Map((organizations.data ?? []).map((organization) => [organization.id, organization.name]));
  const siteById = new Map((sites.data ?? []).map((site) => [site.id, site.name]));
  const assetById = new Map((assets.data ?? []).map((asset) => [asset.id, asset.name]));
  const current = device.data;

  const history = useMemo(() => {
    if (!current) {
      return [];
    }
    return [
      { label: "Criado", value: formatDate(current.created_at) },
      { label: "Status atual", value: current.status },
      { label: "Telemetria", value: telemetry.data ? formatDate(telemetry.data.ultima_atualizacao) : "-" },
    ];
  }, [current, telemetry.data]);

  if (!current) {
    return (
      <div className="space-y-6">
        <PageHeader eyebrow="Devices" title="Detalhes" />
        <Panel>
          <p className="text-sm text-slate-400">{device.isLoading ? "Carregando..." : "Device nao encontrado."}</p>
        </Panel>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader eyebrow="Devices" title={current.name} />
      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <Panel>
          <div className="grid gap-4 sm:grid-cols-2">
            <InfoItem icon={RadioTower} label="Status" value={current.status} />
            <InfoItem icon={Signal} label="Ultima comunicacao" value={formatDate(telemetry.data?.ultima_atualizacao)} />
            <InfoItem icon={Building2} label="Organization" value={organizationById.get(current.organization_id) ?? "-"} />
            <InfoItem icon={MapPin} label="Site" value={siteById.get(current.site_id) ?? "-"} />
            <InfoItem icon={Factory} label="Asset" value={assetById.get(current.asset_id) ?? "-"} />
            <InfoItem icon={RadioTower} label="Tipo" value={current.type} />
          </div>
        </Panel>
        <Panel>
          <div className="grid gap-3 sm:grid-cols-2">
            <Metric icon={Thermometer} label="Temperatura" value={`${telemetry.data?.temperatura ?? "-"} C`} />
            <Metric icon={BatteryCharging} label="Bateria" value={`${telemetry.data?.bateria ?? "-"}%`} />
            <Metric icon={Fuel} label="Combustivel" value={`${telemetry.data?.combustivel ?? "-"}%`} />
            <Metric icon={Signal} label="RSSI" value={`${telemetry.data?.rssi ?? "-"} dBm`} />
          </div>
        </Panel>
      </section>
      <section className="grid gap-4 lg:grid-cols-[1fr_1fr]">
        <Panel>
          <h3 className="mb-3 text-lg font-semibold tracking-normal text-white">Historico</h3>
          <div className="space-y-2">
            {history.map((event) => (
              <div key={event.label} className="flex items-center justify-between border-t border-white/10 py-3 text-sm">
                <span className="text-slate-400">{event.label}</span>
                <span className="text-slate-100">{event.value}</span>
              </div>
            ))}
          </div>
        </Panel>
        <Panel>
          <h3 className="mb-3 text-lg font-semibold tracking-normal text-white">Alertas</h3>
          <div className="rounded-lg border border-dashed border-white/10 p-6 text-sm text-slate-500">
            Nenhum alerta aberto para este device.
          </div>
        </Panel>
      </section>
    </div>
  );
}

function Table({ headers, children }: { headers: string[]; children: ReactNode }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[42rem] border-collapse">
        <thead>
          <tr className="text-left text-xs uppercase text-slate-500">
            {headers.map((header) => (
              <th key={header} className="px-4 py-3 font-medium">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

function InfoItem({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-3">
      <Icon className="mb-3 h-4 w-4 text-cyan-200" aria-hidden />
      <p className="text-xs uppercase text-slate-500">{label}</p>
      <p className="mt-1 truncate text-sm font-medium text-slate-100">{value}</p>
    </div>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-white/10 bg-black/20 p-4">
      <div className="mb-4 flex items-center justify-between">
        <Icon className="h-5 w-5 text-emerald-200" aria-hidden />
        <StatusPill tone="neutral">{label}</StatusPill>
      </div>
      <p className="text-2xl font-semibold tracking-normal text-white">{value}</p>
    </div>
  );
}
