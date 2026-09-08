const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8200";

export type QuestionType = "text" | "multiple_choice" | "rating";
export type SurveyStatus = "draft" | "published";
export type LocationStatus = "granted" | "denied" | "skipped" | "unavailable";
export type SurveyLanguage = "en" | "so";

export type User = {
  id: number;
  email: string;
  name: string;
  is_superadmin?: boolean;
};

export type Question = {
  id?: number;
  prompt: string;
  question_type: QuestionType;
  options: string[];
  required: boolean;
  position: number;
};

export type Survey = {
  id: number;
  public_id: string;
  title: string;
  description: string;
  status: SurveyStatus;
  collect_location: boolean;
  language?: SurveyLanguage;
  created_at: string;
  updated_at: string;
  questions: Question[];
  response_count: number;
};

export type SurveyListItem = {
  id: number;
  public_id: string;
  title: string;
  description: string;
  status: SurveyStatus;
  collect_location: boolean;
  language?: SurveyLanguage;
  created_at: string;
  updated_at: string;
  question_count: number;
  response_count: number;
  owner_id?: number | null;
  owner_name?: string | null;
  owner_email?: string | null;
};

export type PublicSurvey = {
  public_id: string;
  title: string;
  description: string;
  collect_location: boolean;
  language?: SurveyLanguage;
  questions: Required<Question>[];
  wizard?: boolean;
  sections?: { id: string; title: string; question_ids: number[] }[];
};

export type ResponseOut = {
  id: number;
  submitted_at: string;
  latitude: number | null;
  longitude: number | null;
  accuracy: number | null;
  location_status: LocationStatus;
  answers: {
    question_id: number;
    prompt: string;
    question_type: QuestionType;
    value: string;
  }[];
};

export type SurveyResults = {
  survey: Survey;
  responses: ResponseOut[];
  total: number;
};

function authHeaders(token?: string | null): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...authHeaders(token),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    let detail = "Request failed";
    try {
      const data = await res.json();
      detail = data.detail || detail;
      if (Array.isArray(detail)) {
        detail = detail.map((d: { msg?: string }) => d.msg || String(d)).join(", ");
      }
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return res.json();
  }
  return res.text() as Promise<T>;
}

export const api = {
  register: (body: { email: string; password: string; name: string }) =>
    request<{ access_token: string; user: User }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { email: string; password: string }) =>
    request<{ access_token: string; user: User }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  me: (token: string) => request<User>("/api/auth/me", {}, token),
  listSurveys: (token: string) =>
    request<SurveyListItem[]>("/api/surveys", {}, token),
  createSurvey: (
    token: string,
    body: {
      title: string;
      description: string;
      collect_location: boolean;
      questions: Question[];
    }
  ) =>
    request<Survey>(
      "/api/surveys",
      { method: "POST", body: JSON.stringify(body) },
      token
    ),
  createKenyaElectionsTemplate: (token: string) =>
    request<Survey>(
      "/api/surveys/templates/kenya-elections",
      { method: "POST" },
      token
    ),
  createCanadaRefugeeVisaTemplate: (token: string) =>
    request<Survey>(
      "/api/surveys/templates/canada-refugee-visa",
      { method: "POST" },
      token
    ),
  createGermanyRefugeeVisaTemplate: (token: string) =>
    request<Survey>(
      "/api/surveys/templates/germany-refugee-visa",
      { method: "POST" },
      token
    ),
  createUkRefugeeVisaTemplate: (token: string) =>
    request<Survey>(
      "/api/surveys/templates/uk-refugee-visa",
      { method: "POST" },
      token
    ),
  createAustraliaRefugeeVisaTemplate: (token: string) =>
    request<Survey>(
      "/api/surveys/templates/australia-refugee-visa",
      { method: "POST" },
      token
    ),
  getSurvey: (token: string, id: number) =>
    request<Survey>(`/api/surveys/${id}`, {}, token),
  updateSurvey: (
    token: string,
    id: number,
    body: Partial<{
      title: string;
      description: string;
      status: SurveyStatus;
      collect_location: boolean;
      language: SurveyLanguage;
      questions: Question[];
    }>
  ) =>
    request<Survey>(
      `/api/surveys/${id}`,
      { method: "PUT", body: JSON.stringify(body) },
      token
    ),
  deleteSurvey: (token: string, id: number) =>
    request<{ ok: boolean }>(
      `/api/surveys/${id}`,
      { method: "DELETE" },
      token
    ),
  getPublicSurvey: (publicId: string) =>
    request<PublicSurvey>(`/api/public/surveys/${publicId}`),
  submitResponse: (
    publicId: string,
    body: {
      answers: { question_id: number; value: string }[];
      latitude?: number | null;
      longitude?: number | null;
      accuracy?: number | null;
      location_status: LocationStatus;
    }
  ) =>
    request<{ ok: boolean; response_id: number }>(
      `/api/public/surveys/${publicId}/responses`,
      { method: "POST", body: JSON.stringify(body) }
    ),
  startWizardResponse: (
    publicId: string,
    body: {
      answers: { question_id: number; value: string }[];
      latitude?: number | null;
      longitude?: number | null;
      accuracy?: number | null;
      location_status: LocationStatus;
    }
  ) =>
    request<{ ok: boolean; response_id: number; edit_token: string; status: string }>(
      `/api/public/surveys/${publicId}/responses/start`,
      { method: "POST", body: JSON.stringify(body) }
    ),
  saveWizardStep: (
    publicId: string,
    responseId: number,
    body: {
      edit_token: string;
      answers: { question_id: number; value: string }[];
    }
  ) =>
    request<{ ok: boolean; response_id: number; edit_token: string; status: string }>(
      `/api/public/surveys/${publicId}/responses/${responseId}`,
      { method: "PATCH", body: JSON.stringify(body) }
    ),
  completeWizardResponse: (
    publicId: string,
    responseId: number,
    body: { edit_token: string }
  ) =>
    request<{ ok: boolean; response_id: number; edit_token: string; status: string }>(
      `/api/public/surveys/${publicId}/responses/${responseId}/complete`,
      { method: "POST", body: JSON.stringify(body) }
    ),
  getResults: (token: string, id: number) =>
    request<SurveyResults>(`/api/surveys/${id}/results`, {}, token),
  exportCsvUrl: (id: number) => `${API_BASE}/api/surveys/${id}/export.csv`,
};

export const TOKEN_KEY = "survey_token";
export const USER_KEY = "survey_user";
