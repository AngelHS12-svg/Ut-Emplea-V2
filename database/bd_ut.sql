--
-- PostgreSQL database dump
--

\restrict RhqjiNjCYIVfNDg1UtgB0DDFy9yszJTgOKrxqBCE9cUtg2R4YYMsYn2eQo3LFTE

-- Dumped from database version 17.7
-- Dumped by pg_dump version 17.7

-- Started on 2026-03-04 13:45:17

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16652)
-- Name: candidatos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.candidatos (
    id_candidato integer NOT NULL,
    id_usuario integer NOT NULL,
    nombre character varying(100) NOT NULL,
    apellido_paterno character varying(100),
    apellido_materno character varying(100),
    sexo character varying(20),
    telefono character varying(20),
    id_carrera integer,
    tipo_usuario character varying(20),
    anio_egreso integer,
    cv_url text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estatus character varying(50) DEFAULT 'pendiente'::character varying,
    CONSTRAINT candidatos_tipo_usuario_check CHECK (((tipo_usuario)::text = ANY ((ARRAY['estudiante'::character varying, 'egresado'::character varying])::text[])))
);


ALTER TABLE public.candidatos OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16651)
-- Name: candidatos_id_candidato_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.candidatos_id_candidato_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidatos_id_candidato_seq OWNER TO postgres;

--
-- TOC entry 5052 (class 0 OID 0)
-- Dependencies: 229
-- Name: candidatos_id_candidato_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.candidatos_id_candidato_seq OWNED BY public.candidatos.id_candidato;


--
-- TOC entry 222 (class 1259 OID 16599)
-- Name: carreras; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carreras (
    id_carrera integer NOT NULL,
    nombre character varying(150) NOT NULL,
    descripcion text
);


ALTER TABLE public.carreras OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16598)
-- Name: carreras_id_carrera_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.carreras_id_carrera_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.carreras_id_carrera_seq OWNER TO postgres;

--
-- TOC entry 5053 (class 0 OID 0)
-- Dependencies: 221
-- Name: carreras_id_carrera_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.carreras_id_carrera_seq OWNED BY public.carreras.id_carrera;


--
-- TOC entry 226 (class 1259 OID 16626)
-- Name: direcciones_empresa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.direcciones_empresa (
    id_direccion integer NOT NULL,
    id_empresa integer NOT NULL,
    calle character varying(150),
    numero character varying(20),
    colonia character varying(150),
    ciudad character varying(150),
    estado character varying(150),
    codigo_postal character varying(10)
);


ALTER TABLE public.direcciones_empresa OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16625)
-- Name: direcciones_empresa_id_direccion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.direcciones_empresa_id_direccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.direcciones_empresa_id_direccion_seq OWNER TO postgres;

--
-- TOC entry 5054 (class 0 OID 0)
-- Dependencies: 225
-- Name: direcciones_empresa_id_direccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.direcciones_empresa_id_direccion_seq OWNED BY public.direcciones_empresa.id_direccion;


--
-- TOC entry 224 (class 1259 OID 16608)
-- Name: empresas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.empresas (
    id_empresa integer NOT NULL,
    id_usuario integer NOT NULL,
    nombre character varying(150) NOT NULL,
    giro character varying(150),
    tipo_empresa character varying(100),
    telefono character varying(20),
    descripcion text,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estatus character varying(50) DEFAULT 'pendiente'::character varying
);


ALTER TABLE public.empresas OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16607)
-- Name: empresas_id_empresa_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.empresas_id_empresa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.empresas_id_empresa_seq OWNER TO postgres;

--
-- TOC entry 5055 (class 0 OID 0)
-- Dependencies: 223
-- Name: empresas_id_empresa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.empresas_id_empresa_seq OWNED BY public.empresas.id_empresa;


--
-- TOC entry 238 (class 1259 OID 16727)
-- Name: historial_postulacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.historial_postulacion (
    id_historial integer NOT NULL,
    id_postulacion integer NOT NULL,
    estado character varying(50),
    comentario text,
    fecha timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.historial_postulacion OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16726)
-- Name: historial_postulacion_id_historial_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.historial_postulacion_id_historial_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historial_postulacion_id_historial_seq OWNER TO postgres;

--
-- TOC entry 5056 (class 0 OID 0)
-- Dependencies: 237
-- Name: historial_postulacion_id_historial_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.historial_postulacion_id_historial_seq OWNED BY public.historial_postulacion.id_historial;


--
-- TOC entry 236 (class 1259 OID 16706)
-- Name: postulaciones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.postulaciones (
    id_postulacion integer NOT NULL,
    id_vacante integer NOT NULL,
    id_candidato integer NOT NULL,
    fecha_postulacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado character varying(50) DEFAULT 'en revision'::character varying,
    comentarios text,
    fecha_actualizacion timestamp without time zone
);


ALTER TABLE public.postulaciones OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16705)
-- Name: postulaciones_id_postulacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.postulaciones_id_postulacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.postulaciones_id_postulacion_seq OWNER TO postgres;

--
-- TOC entry 5057 (class 0 OID 0)
-- Dependencies: 235
-- Name: postulaciones_id_postulacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.postulaciones_id_postulacion_seq OWNED BY public.postulaciones.id_postulacion;


--
-- TOC entry 228 (class 1259 OID 16640)
-- Name: recursos_humanos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.recursos_humanos (
    id_rh integer NOT NULL,
    id_empresa integer NOT NULL,
    nombre character varying(150) NOT NULL,
    telefono character varying(20),
    correo character varying(150)
);


ALTER TABLE public.recursos_humanos OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16639)
-- Name: recursos_humanos_id_rh_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recursos_humanos_id_rh_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recursos_humanos_id_rh_seq OWNER TO postgres;

--
-- TOC entry 5058 (class 0 OID 0)
-- Dependencies: 227
-- Name: recursos_humanos_id_rh_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.recursos_humanos_id_rh_seq OWNED BY public.recursos_humanos.id_rh;


--
-- TOC entry 234 (class 1259 OID 16692)
-- Name: requisitos_vacante; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.requisitos_vacante (
    id_requisito integer NOT NULL,
    id_vacante integer NOT NULL,
    escolaridad character varying(150),
    experiencia character varying(150),
    descripcion text
);


ALTER TABLE public.requisitos_vacante OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16691)
-- Name: requisitos_vacante_id_requisito_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.requisitos_vacante_id_requisito_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.requisitos_vacante_id_requisito_seq OWNER TO postgres;

--
-- TOC entry 5059 (class 0 OID 0)
-- Dependencies: 233
-- Name: requisitos_vacante_id_requisito_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.requisitos_vacante_id_requisito_seq OWNED BY public.requisitos_vacante.id_requisito;


--
-- TOC entry 218 (class 1259 OID 16572)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id_rol integer NOT NULL,
    nombre character varying(50) NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16571)
-- Name: roles_id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_rol_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_rol_seq OWNER TO postgres;

--
-- TOC entry 5060 (class 0 OID 0)
-- Dependencies: 217
-- Name: roles_id_rol_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_rol_seq OWNED BY public.roles.id_rol;


--
-- TOC entry 220 (class 1259 OID 16581)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id_usuario integer NOT NULL,
    id_rol integer NOT NULL,
    correo character varying(150) NOT NULL,
    password text NOT NULL,
    fecha_registro timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    activo boolean DEFAULT true
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16580)
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuarios_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usuarios_id_usuario_seq OWNER TO postgres;

--
-- TOC entry 5061 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.usuarios_id_usuario_seq OWNED BY public.usuarios.id_usuario;


--
-- TOC entry 232 (class 1259 OID 16676)
-- Name: vacantes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vacantes (
    id_vacante integer NOT NULL,
    id_empresa integer NOT NULL,
    titulo character varying(150) NOT NULL,
    descripcion text NOT NULL,
    salario numeric(10,2),
    modalidad character varying(50),
    horario character varying(100),
    lugar_trabajo character varying(150),
    fecha_publicacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento date,
    estatus character varying(50) DEFAULT 'activa'::character varying
);


ALTER TABLE public.vacantes OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16675)
-- Name: vacantes_id_vacante_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vacantes_id_vacante_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.vacantes_id_vacante_seq OWNER TO postgres;

--
-- TOC entry 5062 (class 0 OID 0)
-- Dependencies: 231
-- Name: vacantes_id_vacante_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vacantes_id_vacante_seq OWNED BY public.vacantes.id_vacante;


--
-- TOC entry 242 (class 1259 OID 16757)
-- Name: validacion_candidatos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.validacion_candidatos (
    id_validacion integer NOT NULL,
    id_candidato integer NOT NULL,
    aprobado boolean,
    comentario text,
    fecha_validacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.validacion_candidatos OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16756)
-- Name: validacion_candidatos_id_validacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.validacion_candidatos_id_validacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.validacion_candidatos_id_validacion_seq OWNER TO postgres;

--
-- TOC entry 5063 (class 0 OID 0)
-- Dependencies: 241
-- Name: validacion_candidatos_id_validacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.validacion_candidatos_id_validacion_seq OWNED BY public.validacion_candidatos.id_validacion;


--
-- TOC entry 240 (class 1259 OID 16742)
-- Name: validacion_empresas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.validacion_empresas (
    id_validacion integer NOT NULL,
    id_empresa integer NOT NULL,
    aprobado boolean,
    comentario text,
    fecha_validacion timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.validacion_empresas OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16741)
-- Name: validacion_empresas_id_validacion_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.validacion_empresas_id_validacion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.validacion_empresas_id_validacion_seq OWNER TO postgres;

--
-- TOC entry 5064 (class 0 OID 0)
-- Dependencies: 239
-- Name: validacion_empresas_id_validacion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.validacion_empresas_id_validacion_seq OWNED BY public.validacion_empresas.id_validacion;


--
-- TOC entry 4812 (class 2604 OID 16655)
-- Name: candidatos id_candidato; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos ALTER COLUMN id_candidato SET DEFAULT nextval('public.candidatos_id_candidato_seq'::regclass);


--
-- TOC entry 4806 (class 2604 OID 16602)
-- Name: carreras id_carrera; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreras ALTER COLUMN id_carrera SET DEFAULT nextval('public.carreras_id_carrera_seq'::regclass);


--
-- TOC entry 4810 (class 2604 OID 16629)
-- Name: direcciones_empresa id_direccion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direcciones_empresa ALTER COLUMN id_direccion SET DEFAULT nextval('public.direcciones_empresa_id_direccion_seq'::regclass);


--
-- TOC entry 4807 (class 2604 OID 16611)
-- Name: empresas id_empresa; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresas ALTER COLUMN id_empresa SET DEFAULT nextval('public.empresas_id_empresa_seq'::regclass);


--
-- TOC entry 4822 (class 2604 OID 16730)
-- Name: historial_postulacion id_historial; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_postulacion ALTER COLUMN id_historial SET DEFAULT nextval('public.historial_postulacion_id_historial_seq'::regclass);


--
-- TOC entry 4819 (class 2604 OID 16709)
-- Name: postulaciones id_postulacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postulaciones ALTER COLUMN id_postulacion SET DEFAULT nextval('public.postulaciones_id_postulacion_seq'::regclass);


--
-- TOC entry 4811 (class 2604 OID 16643)
-- Name: recursos_humanos id_rh; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos_humanos ALTER COLUMN id_rh SET DEFAULT nextval('public.recursos_humanos_id_rh_seq'::regclass);


--
-- TOC entry 4818 (class 2604 OID 16695)
-- Name: requisitos_vacante id_requisito; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.requisitos_vacante ALTER COLUMN id_requisito SET DEFAULT nextval('public.requisitos_vacante_id_requisito_seq'::regclass);


--
-- TOC entry 4802 (class 2604 OID 16575)
-- Name: roles id_rol; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id_rol SET DEFAULT nextval('public.roles_id_rol_seq'::regclass);


--
-- TOC entry 4803 (class 2604 OID 16584)
-- Name: usuarios id_usuario; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuarios_id_usuario_seq'::regclass);


--
-- TOC entry 4815 (class 2604 OID 16679)
-- Name: vacantes id_vacante; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacantes ALTER COLUMN id_vacante SET DEFAULT nextval('public.vacantes_id_vacante_seq'::regclass);


--
-- TOC entry 4826 (class 2604 OID 16760)
-- Name: validacion_candidatos id_validacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_candidatos ALTER COLUMN id_validacion SET DEFAULT nextval('public.validacion_candidatos_id_validacion_seq'::regclass);


--
-- TOC entry 4824 (class 2604 OID 16745)
-- Name: validacion_empresas id_validacion; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_empresas ALTER COLUMN id_validacion SET DEFAULT nextval('public.validacion_empresas_id_validacion_seq'::regclass);


--
-- TOC entry 5034 (class 0 OID 16652)
-- Dependencies: 230
-- Data for Name: candidatos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.candidatos (id_candidato, id_usuario, nombre, apellido_paterno, apellido_materno, sexo, telefono, id_carrera, tipo_usuario, anio_egreso, cv_url, fecha_registro, estatus) FROM stdin;
\.


--
-- TOC entry 5026 (class 0 OID 16599)
-- Dependencies: 222
-- Data for Name: carreras; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.carreras (id_carrera, nombre, descripcion) FROM stdin;
\.


--
-- TOC entry 5030 (class 0 OID 16626)
-- Dependencies: 226
-- Data for Name: direcciones_empresa; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.direcciones_empresa (id_direccion, id_empresa, calle, numero, colonia, ciudad, estado, codigo_postal) FROM stdin;
\.


--
-- TOC entry 5028 (class 0 OID 16608)
-- Dependencies: 224
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.empresas (id_empresa, id_usuario, nombre, giro, tipo_empresa, telefono, descripcion, fecha_registro, estatus) FROM stdin;
\.


--
-- TOC entry 5042 (class 0 OID 16727)
-- Dependencies: 238
-- Data for Name: historial_postulacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.historial_postulacion (id_historial, id_postulacion, estado, comentario, fecha) FROM stdin;
\.


--
-- TOC entry 5040 (class 0 OID 16706)
-- Dependencies: 236
-- Data for Name: postulaciones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.postulaciones (id_postulacion, id_vacante, id_candidato, fecha_postulacion, estado, comentarios, fecha_actualizacion) FROM stdin;
\.


--
-- TOC entry 5032 (class 0 OID 16640)
-- Dependencies: 228
-- Data for Name: recursos_humanos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.recursos_humanos (id_rh, id_empresa, nombre, telefono, correo) FROM stdin;
\.


--
-- TOC entry 5038 (class 0 OID 16692)
-- Dependencies: 234
-- Data for Name: requisitos_vacante; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.requisitos_vacante (id_requisito, id_vacante, escolaridad, experiencia, descripcion) FROM stdin;
\.


--
-- TOC entry 5022 (class 0 OID 16572)
-- Dependencies: 218
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id_rol, nombre) FROM stdin;
1	Administrador
2	Empresa
3	Candidato
\.


--
-- TOC entry 5024 (class 0 OID 16581)
-- Dependencies: 220
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id_usuario, id_rol, correo, password, fecha_registro, activo) FROM stdin;
\.


--
-- TOC entry 5036 (class 0 OID 16676)
-- Dependencies: 232
-- Data for Name: vacantes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vacantes (id_vacante, id_empresa, titulo, descripcion, salario, modalidad, horario, lugar_trabajo, fecha_publicacion, fecha_vencimiento, estatus) FROM stdin;
\.


--
-- TOC entry 5046 (class 0 OID 16757)
-- Dependencies: 242
-- Data for Name: validacion_candidatos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.validacion_candidatos (id_validacion, id_candidato, aprobado, comentario, fecha_validacion) FROM stdin;
\.


--
-- TOC entry 5044 (class 0 OID 16742)
-- Dependencies: 240
-- Data for Name: validacion_empresas; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.validacion_empresas (id_validacion, id_empresa, aprobado, comentario, fecha_validacion) FROM stdin;
\.


--
-- TOC entry 5065 (class 0 OID 0)
-- Dependencies: 229
-- Name: candidatos_id_candidato_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.candidatos_id_candidato_seq', 1, false);


--
-- TOC entry 5066 (class 0 OID 0)
-- Dependencies: 221
-- Name: carreras_id_carrera_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carreras_id_carrera_seq', 1, false);


--
-- TOC entry 5067 (class 0 OID 0)
-- Dependencies: 225
-- Name: direcciones_empresa_id_direccion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.direcciones_empresa_id_direccion_seq', 1, false);


--
-- TOC entry 5068 (class 0 OID 0)
-- Dependencies: 223
-- Name: empresas_id_empresa_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.empresas_id_empresa_seq', 1, false);


--
-- TOC entry 5069 (class 0 OID 0)
-- Dependencies: 237
-- Name: historial_postulacion_id_historial_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.historial_postulacion_id_historial_seq', 1, false);


--
-- TOC entry 5070 (class 0 OID 0)
-- Dependencies: 235
-- Name: postulaciones_id_postulacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.postulaciones_id_postulacion_seq', 1, false);


--
-- TOC entry 5071 (class 0 OID 0)
-- Dependencies: 227
-- Name: recursos_humanos_id_rh_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recursos_humanos_id_rh_seq', 1, false);


--
-- TOC entry 5072 (class 0 OID 0)
-- Dependencies: 233
-- Name: requisitos_vacante_id_requisito_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.requisitos_vacante_id_requisito_seq', 1, false);


--
-- TOC entry 5073 (class 0 OID 0)
-- Dependencies: 217
-- Name: roles_id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_rol_seq', 3, true);


--
-- TOC entry 5074 (class 0 OID 0)
-- Dependencies: 219
-- Name: usuarios_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuarios_id_usuario_seq', 1, false);


--
-- TOC entry 5075 (class 0 OID 0)
-- Dependencies: 231
-- Name: vacantes_id_vacante_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vacantes_id_vacante_seq', 1, false);


--
-- TOC entry 5076 (class 0 OID 0)
-- Dependencies: 241
-- Name: validacion_candidatos_id_validacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.validacion_candidatos_id_validacion_seq', 1, false);


--
-- TOC entry 5077 (class 0 OID 0)
-- Dependencies: 239
-- Name: validacion_empresas_id_validacion_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.validacion_empresas_id_validacion_seq', 1, false);


--
-- TOC entry 4848 (class 2606 OID 16664)
-- Name: candidatos candidatos_id_usuario_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_id_usuario_key UNIQUE (id_usuario);


--
-- TOC entry 4850 (class 2606 OID 16662)
-- Name: candidatos candidatos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_pkey PRIMARY KEY (id_candidato);


--
-- TOC entry 4838 (class 2606 OID 16606)
-- Name: carreras carreras_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreras
    ADD CONSTRAINT carreras_pkey PRIMARY KEY (id_carrera);


--
-- TOC entry 4844 (class 2606 OID 16633)
-- Name: direcciones_empresa direcciones_empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direcciones_empresa
    ADD CONSTRAINT direcciones_empresa_pkey PRIMARY KEY (id_direccion);


--
-- TOC entry 4840 (class 2606 OID 16619)
-- Name: empresas empresas_id_usuario_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_id_usuario_key UNIQUE (id_usuario);


--
-- TOC entry 4842 (class 2606 OID 16617)
-- Name: empresas empresas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_pkey PRIMARY KEY (id_empresa);


--
-- TOC entry 4858 (class 2606 OID 16735)
-- Name: historial_postulacion historial_postulacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_postulacion
    ADD CONSTRAINT historial_postulacion_pkey PRIMARY KEY (id_historial);


--
-- TOC entry 4856 (class 2606 OID 16715)
-- Name: postulaciones postulaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postulaciones
    ADD CONSTRAINT postulaciones_pkey PRIMARY KEY (id_postulacion);


--
-- TOC entry 4846 (class 2606 OID 16645)
-- Name: recursos_humanos recursos_humanos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos_humanos
    ADD CONSTRAINT recursos_humanos_pkey PRIMARY KEY (id_rh);


--
-- TOC entry 4854 (class 2606 OID 16699)
-- Name: requisitos_vacante requisitos_vacante_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.requisitos_vacante
    ADD CONSTRAINT requisitos_vacante_pkey PRIMARY KEY (id_requisito);


--
-- TOC entry 4830 (class 2606 OID 16579)
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- TOC entry 4832 (class 2606 OID 16577)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- TOC entry 4834 (class 2606 OID 16592)
-- Name: usuarios usuarios_correo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_correo_key UNIQUE (correo);


--
-- TOC entry 4836 (class 2606 OID 16590)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4852 (class 2606 OID 16685)
-- Name: vacantes vacantes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacantes
    ADD CONSTRAINT vacantes_pkey PRIMARY KEY (id_vacante);


--
-- TOC entry 4862 (class 2606 OID 16765)
-- Name: validacion_candidatos validacion_candidatos_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_candidatos
    ADD CONSTRAINT validacion_candidatos_pkey PRIMARY KEY (id_validacion);


--
-- TOC entry 4860 (class 2606 OID 16750)
-- Name: validacion_empresas validacion_empresas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_empresas
    ADD CONSTRAINT validacion_empresas_pkey PRIMARY KEY (id_validacion);


--
-- TOC entry 4867 (class 2606 OID 16670)
-- Name: candidatos candidatos_id_carrera_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_id_carrera_fkey FOREIGN KEY (id_carrera) REFERENCES public.carreras(id_carrera);


--
-- TOC entry 4868 (class 2606 OID 16665)
-- Name: candidatos candidatos_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.candidatos
    ADD CONSTRAINT candidatos_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4865 (class 2606 OID 16634)
-- Name: direcciones_empresa direcciones_empresa_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.direcciones_empresa
    ADD CONSTRAINT direcciones_empresa_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresas(id_empresa) ON DELETE CASCADE;


--
-- TOC entry 4864 (class 2606 OID 16620)
-- Name: empresas empresas_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4873 (class 2606 OID 16736)
-- Name: historial_postulacion historial_postulacion_id_postulacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.historial_postulacion
    ADD CONSTRAINT historial_postulacion_id_postulacion_fkey FOREIGN KEY (id_postulacion) REFERENCES public.postulaciones(id_postulacion) ON DELETE CASCADE;


--
-- TOC entry 4871 (class 2606 OID 16721)
-- Name: postulaciones postulaciones_id_candidato_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postulaciones
    ADD CONSTRAINT postulaciones_id_candidato_fkey FOREIGN KEY (id_candidato) REFERENCES public.candidatos(id_candidato) ON DELETE CASCADE;


--
-- TOC entry 4872 (class 2606 OID 16716)
-- Name: postulaciones postulaciones_id_vacante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.postulaciones
    ADD CONSTRAINT postulaciones_id_vacante_fkey FOREIGN KEY (id_vacante) REFERENCES public.vacantes(id_vacante) ON DELETE CASCADE;


--
-- TOC entry 4866 (class 2606 OID 16646)
-- Name: recursos_humanos recursos_humanos_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.recursos_humanos
    ADD CONSTRAINT recursos_humanos_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresas(id_empresa) ON DELETE CASCADE;


--
-- TOC entry 4870 (class 2606 OID 16700)
-- Name: requisitos_vacante requisitos_vacante_id_vacante_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.requisitos_vacante
    ADD CONSTRAINT requisitos_vacante_id_vacante_fkey FOREIGN KEY (id_vacante) REFERENCES public.vacantes(id_vacante) ON DELETE CASCADE;


--
-- TOC entry 4863 (class 2606 OID 16593)
-- Name: usuarios usuarios_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.roles(id_rol);


--
-- TOC entry 4869 (class 2606 OID 16686)
-- Name: vacantes vacantes_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacantes
    ADD CONSTRAINT vacantes_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresas(id_empresa) ON DELETE CASCADE;


--
-- TOC entry 4875 (class 2606 OID 16766)
-- Name: validacion_candidatos validacion_candidatos_id_candidato_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_candidatos
    ADD CONSTRAINT validacion_candidatos_id_candidato_fkey FOREIGN KEY (id_candidato) REFERENCES public.candidatos(id_candidato) ON DELETE CASCADE;


--
-- TOC entry 4874 (class 2606 OID 16751)
-- Name: validacion_empresas validacion_empresas_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.validacion_empresas
    ADD CONSTRAINT validacion_empresas_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresas(id_empresa) ON DELETE CASCADE;


-- Completed on 2026-03-04 13:45:17

--
-- PostgreSQL database dump complete
--

\unrestrict RhqjiNjCYIVfNDg1UtgB0DDFy9yszJTgOKrxqBCE9cUtg2R4YYMsYn2eQo3LFTE

