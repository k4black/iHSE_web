--
-- PostgreSQL database dump
--

-- Dumped from database version 12.1 (Debian 12.1-1.pgdg100+1)
-- Dumped by pg_dump version 12.1 (Debian 12.1-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: random_bytea(integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.random_bytea(bytea_length integer) RETURNS bytea
    LANGUAGE sql
    AS $_$
            SELECT decode(string_agg(lpad(to_hex(width_bucket(random(), 0, 1, 256)-1),2,'0') ,''), 'hex')
            FROM generate_series(1, $1);
            $_$;


ALTER FUNCTION public.random_bytea(bytea_length integer) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: classes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.classes (
    id integer NOT NULL,
    total integer DEFAULT 0,
    annotation text DEFAULT ''::text
);


ALTER TABLE public.classes OWNER TO postgres;

--
-- Name: codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.codes (
    id integer NOT NULL,
    code text,
    type integer DEFAULT 0,
    used boolean DEFAULT false
);


ALTER TABLE public.codes OWNER TO postgres;

--
-- Name: codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.codes_id_seq OWNER TO postgres;

--
-- Name: codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.codes_id_seq OWNED BY public.codes.id;


--
-- Name: credits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credits (
    id integer NOT NULL,
    user_id integer,
    event_id integer,
    "time" text DEFAULT ''::text,
    value integer DEFAULT 0
);


ALTER TABLE public.credits OWNER TO postgres;

--
-- Name: credits_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.credits_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.credits_id_seq OWNER TO postgres;

--
-- Name: credits_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.credits_id_seq OWNED BY public.credits.id;


--
-- Name: days; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.days (
    id integer NOT NULL,
    date text DEFAULT ''::text,
    title text DEFAULT ''::text,
    feedback boolean DEFAULT false
);


ALTER TABLE public.days OWNER TO postgres;

--
-- Name: days_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.days_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.days_id_seq OWNER TO postgres;

--
-- Name: days_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.days_id_seq OWNED BY public.days.id;


--
-- Name: enrolls; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enrolls (
    id integer NOT NULL,
    class_id integer,
    user_id integer,
    "time" text DEFAULT ''::text,
    attendance boolean DEFAULT false,
    bonus integer DEFAULT 0
);


ALTER TABLE public.enrolls OWNER TO postgres;

--
-- Name: enrolls_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.enrolls_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.enrolls_id_seq OWNER TO postgres;

--
-- Name: enrolls_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.enrolls_id_seq OWNED BY public.enrolls.id;


--
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id integer NOT NULL,
    type integer,
    title text DEFAULT ''::text,
    description text DEFAULT ''::text,
    host text DEFAULT ''::text,
    place text DEFAULT ''::text,
    "time" text DEFAULT ''::text,
    day_id integer
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO postgres;

--
-- Name: events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq OWNED BY public.events.id;


--
-- Name: feedback; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feedback (
    id integer NOT NULL,
    user_id integer,
    event_id integer,
    score integer,
    entertain integer,
    useful integer,
    understand integer,
    comment text DEFAULT ''::text
);


ALTER TABLE public.feedback OWNER TO postgres;

--
-- Name: feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feedback_id_seq OWNER TO postgres;

--
-- Name: feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feedback_id_seq OWNED BY public.feedback.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    title text DEFAULT ''::text,
    type text DEFAULT ''::text,
    def_type text DEFAULT ''::text,
    direction text DEFAULT ''::text,
    description text DEFAULT ''::text,
    annotation text DEFAULT ''::text
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projects_id_seq OWNER TO postgres;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    id bytea DEFAULT public.random_bytea(16) NOT NULL,
    user_id integer,
    user_type integer DEFAULT 0,
    user_agent text DEFAULT ''::text,
    last_ip text DEFAULT ''::text,
    "time" text DEFAULT ''::text
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: top; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.top (
    id integer NOT NULL,
    user_id integer,
    day_id integer,
    chosen_1 integer,
    chosen_2 integer,
    chosen_3 integer
);


ALTER TABLE public.top OWNER TO postgres;

--
-- Name: top_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.top_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.top_id_seq OWNER TO postgres;

--
-- Name: top_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.top_id_seq OWNED BY public.top.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    code text NOT NULL,
    user_type integer DEFAULT 0,
    phone text DEFAULT ''::text,
    name text DEFAULT ''::text,
    sex boolean,
    pass integer,
    team integer DEFAULT 0,
    project_id integer DEFAULT 0,
    avatar text DEFAULT ''::text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vacations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vacations (
    id integer NOT NULL,
    user_id integer,
    date_from text DEFAULT ''::text,
    date_to text DEFAULT ''::text,
    time_from text DEFAULT ''::text,
    time_to text DEFAULT ''::text
);


ALTER TABLE public.vacations OWNER TO postgres;

--
-- Name: vacations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vacations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vacations_id_seq OWNER TO postgres;

--
-- Name: vacations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vacations_id_seq OWNED BY public.vacations.id;


--
-- Name: codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes ALTER COLUMN id SET DEFAULT nextval('public.codes_id_seq'::regclass);


--
-- Name: credits id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits ALTER COLUMN id SET DEFAULT nextval('public.credits_id_seq'::regclass);


--
-- Name: days id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.days ALTER COLUMN id SET DEFAULT nextval('public.days_id_seq'::regclass);


--
-- Name: enrolls id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrolls ALTER COLUMN id SET DEFAULT nextval('public.enrolls_id_seq'::regclass);


--
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq'::regclass);


--
-- Name: feedback id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback ALTER COLUMN id SET DEFAULT nextval('public.feedback_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: top id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top ALTER COLUMN id SET DEFAULT nextval('public.top_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vacations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacations ALTER COLUMN id SET DEFAULT nextval('public.vacations_id_seq'::regclass);


--
-- Data for Name: classes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.classes (id, total, annotation) FROM stdin;
8	0	
11	0	
13	0	
21	0	
22	0	
23	0	
24	0	
27	0	
28	0	
30	0	
29	0	
35	0	
36	0	
37	0	
38	0	
39	0	
42	0	
43	0	
44	0	
45	0	
47	0	
48	0	
49	0	
50	0	
51	0	
53	0	
\.


--
-- Data for Name: codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.codes (id, code, type, used) FROM stdin;
2	J25B1C	0	f
4	B6J63S	0	f
5	6AU016	0	f
6	BXD832	0	f
8	76E0QY	0	f
10	E0524G	0	f
12	ACLKDP	0	f
13	W7NM92	0	f
15	T0793X	0	f
18	43X3Q1	0	f
19	ZY1ITA	0	f
20	J942VC	0	f
1	Y2G41J	0	t
7	Q920M7	0	t
11	1857L4	0	t
14	VW4946	0	t
9	MPJ840	0	t
3	F7Q6T4	0	t
16	SOG6Q4	0	t
17	TYW7H9	0	t
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credits (id, user_id, event_id, "time", value) FROM stdin;
\.


--
-- Data for Name: days; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.days (id, date, title, feedback) FROM stdin;
0	NO DAY		f
1	05.06		f
2	06.06		f
4	08.06		f
5	09.06		f
7	11.06		f
3	07.06		t
6	10.06		t
8	12.06		f
9	13.06		t
\.


--
-- Data for Name: enrolls; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.enrolls (id, class_id, user_id, "time", attendance, bonus) FROM stdin;
\.


--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, type, title, description, host, place, "time", day_id) FROM stdin;
2	0	Трансфер НИУ ВШЭ - "Чайка"				10.00\n11.00	1
3	0	Размещение по корпусам, знакомство в отрядах				11.00\n12.50	1
4	0	Обед // Отдых				13.00\n14.00	1
6	0	Полдник				16.00\n16.10	1
7	0	Баня // Отдых				16.10\n17.30	1
8	1	Проектирование досуговых мероприятий в лагере		Ксения Бурлак	Дача № 3, подъезд 2, ком.3	17.30\n19.00	1
10	0	Ужин				19.00\n19.30	1
13	2	Легенда лагеря – Школьный университет «iВышка»		А.А. Бляхман, Н.А. Серова	КЛУБ	20.10\n21.00	1
14	0	Кефир				21.00\n21.10	1
11	1	Танцуй, iВышка!		Лада Зотова	Танц.площадка	19.30\n20.00	1
16	0	Рефлексия				22.20\n22.45	1
17	0	Отбой				23.00	1
15	3	Спевка		Вожатые	ЗАЛ (столовая)	21.10\n22.10	1
12	3	Подготовка к концерту «Таланты iВышки»			Отрядные комнаты	19.30\n20.00	1
9	3	Подготовка к концерту «Таланты iВышки»		Все участники смены	Отрядные комнаты	17.30\n19.00	1
5	3	Верёвочный курс		Вожатые	Линейка	14.00\n16.00	1
1	3	Регистрация отъежающих в лагерь	Фотографирование		НИУ ВШЭ, Большая Печерская, 25/12	8.30\n10.00	1
18	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	2
19	0	Сбор отрядов			Линейка	8.50	2
20	0	Завтрак				9.00\n10.00	2
21	2	Всё о проектах	Проектная работа: установочная сессия	Екатерина Прохорова	ЗАЛ (столовая)	10.00\n11.20	2
22	2	iВышка - участник  "Проект 800"	О содержании проектной и исследовательской деятельности	Милана Евстигнеева	Клуб	10.00\n11.20	2
23	2	iВышка - участник  "Проект 800"	О содержании проектной и исследовательской деятельности	Милана Евстигнеева	Клуб	11.30\n12.50	2
24	2	Всё о проектах	Проектная работа: установочная сессия	Екатерина Прохорова	ЗАЛ (столовая)	11.30\n12.50	2
26	0	Баня // Отдых				13.30\n14.30	2
25	0	Обед				13.00\n14.00	2
27	1	"Опять об Пушкине!"	Пушкин как литературный герой	М.М. Гельфонд	ЗАЛ (столовая)	14.30\n16.00	2
28	1	Все врут	или что в действительности нужно клиентам вашего бизнеса	Д.В. Сидоров	Клуб	14.30\n16.00	2
30	1	Проектирование досуговых мероприятий в лагере		Ксения Бурлак	Корпус 3, подъезд 2, ком.1	14.30\n16.00	2
31	0	Полдник				16.00\n16.10	2
43	1	Программирование без компьютеров	Занятие 1-1	Ирина Саблина	Кирпич. здание, 2 этаж	14.30\n15.50	3
29	2	Исследование & проект: в чем отличие?	Исследовательская работа: установочная сессия	Милана Евстигнеева	Комп.класс №1	14.30\n16.00	2
32	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	3
33	0	Сбор отрядов			Линейка	8.50	3
34	0	Завтрак				9.00\n10.00	3
35	2	Экономический рост или экологическая катастрофа? Что мы делаем не так?		А.С. Аладышкина	ЗАЛ (столовая)	10.00\n11.20	3
36	2	Презумпции и фикции в праве		А.В. Козлов	КЛУБ	10.00\n11.20	3
37	2	Презумпции и фикции в праве		А.В. Козлов	КЛУБ	11.30\n12.50	3
38	2	Экономический рост или экологическая катастрофа? Что мы делаем не так?		А.С. Аладышкина	ЗАЛ (столовая)	11.30\n12.50	3
39	2	Межкультурная коммуникация в современном мире		В.Г. Зусман	"Большая стекляшка"	11.30\n12.50	3
40	0	Обед				13.00\n14.00	3
41	0	Баня // Отдых				13.30\n14.30	3
42	1	iМедиа & iNews	Занятие 1-6	Мариам Мкртумян, Анастасия Кирсанова	"Большая стекляшка"	14.30\n15.50	3
44	1	Школа французского для начинающих	Заняти 1-4	Елизавета Капелева	Комп.класс № 1	14.30\n15.50	3
45	1	Цифровая экономика или почему роботы будут завидовать экономистам?		М.А. Штефан	ЗАЛ (столовая)	14.30\n15.50	3
46	0	Полдник				16.00\n16.10	3
47	1	Школа немецкого	Занятие 1-3	Ирина Мартышкина	Дача 3, подъезд 2. ком. 1	16.10\n17.30	3
48	1	Итоговое сочинение: советы успешного абитуриента	Занятие 1-2	Яна Логинова	"Большая стекляшка"	16.10\n17.30	3
49	1	Уличный театр: кручение "пои"	Занятие 1-3	Константин Чернышев	Танц.площадка	16.10\n17.30	3
50	1	Математика: 19 задание ЕГЭ летом	Заняти 1-3	Михаил Кузнецов	Комп. класс №1	16.10\n17.30	3
51	1	"Танцуем Вальс"	Занятие 1-6\n(обязательное посещение всех шести занятий)	Михаил Кортунов	КЛУБ	16.10\n17.30	3
52	3	Подготовка к вечернему концерту «Таланты iВышки»			Клуб, отрядные комнаты	17.30\n19.00	3
53	1	Бейсбол		Никита Власюк	Фут.поле	17.30\n19.00	3
54	0	Ужин				19.00\n19.30	3
55	3	Подготовка к вечернему концерту «Таланты iВышки»				19.30\n20.00	3
56	3	Концерт «Таланты iВышки»	Перерыв (Кефир): 21.00 – 21.10		КЛУБ	20.15\n22.00	3
57	0	Рефлексия				22.20\n22.45	3
58	0	Отбой				23.00	3
\.


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.feedback (id, user_id, event_id, score, entertain, useful, understand, comment) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, title, type, def_type, direction, description, annotation) FROM stdin;
0	NO PROJECT					
1	Умные остановки	project	presentation	media	Описание проекта умных остановок, который довольно большой. Тут должны описываться общие этапы.	Делаем умные остановки для нижнего
2	Цифровой Нижний	science	TED	IT	Модульная система обеспечивающая связь между администрацией и жителями Нижнего Новгорода.	Связь между администрацией и жителями.
3	Неформальный Нижний Новгород	other	TED	tourism	Этот проект будет посвящен местам в Нижнем Новгороде, о которых вы не задумывались ранее, но которые будут интересны всем вам. 	Путеводитель по Нижнему.
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (id, user_id, user_type, user_agent, last_ip, "time") FROM stdin;
\\xeafb895cab901465958e63ac2bdbe4c1	0	2	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.5 Safari/605.1.15	172.18.0.1	2020-02-28 13:46:30 MSK
\\x4016b8e46225bfa082fac7b38e8d0c42	1	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:38:25 MSK
\\x7005ebcae0ad74dc6a6b8ded9706390b	2	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:43:41 MSK
\\xa869efe1208a5af0b940d4b344fca64e	3	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:44:46 MSK
\\xe06dbd7b9769679dc0335e685a80cb4d	4	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:53:47 MSK
\\x02b1c3fd545774a3b521799ddc05ed6f	5	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:55:18 MSK
\\xf6e705d7f70cc10c66d116eb7cb7fc61	6	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 08:56:17 MSK
\\x9bce19a65bc96e1d592a005c086f52a7	7	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 09:07:38 MSK
\\xcf29ac0d999518ee1bc72b81067e0316	8	0	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 09:08:48 MSK
\\xcb06c48662d5364106228b7adaf2bb08	0	2	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36	172.18.0.1	2020-02-24 09:08:50 MSK
\.


--
-- Data for Name: top; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.top (id, user_id, day_id, chosen_1, chosen_2, chosen_3) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, code, user_type, phone, name, sex, pass, team, project_id, avatar) FROM stdin;
1	Y2G41J	0	79157043031	Юлия Самойлова	f	105934	4	0	non
2	Q920M7	0	79874289399	Игорь Прокопенко	t	105934	1	0	non
6	F7Q6T4	0	79353522345	Максим Чернявский	t	105934	4	0	non
3	1857L4	0	79441231233	Василина Петровна	f	105934	4	2	non
7	SOG6Q4	0	79266784848	Александр Никифоров	t	105934	3	3	non
5	MPJ840	0	79776664529	Оксана Антипова	f	105934	2	1	non
4	VW4946	0	79645266448	Евгения Зитцева	t	105934	4	2	non
8	TYW7H9	0	79984772664	Анастасия Кревенко	f	105934	5	2	non
0	TECODE	2	72345678900	Admin Userer	t	105934	0	0	non
\.


--
-- Data for Name: vacations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vacations (id, user_id, date_from, date_to, time_from, time_to) FROM stdin;
\.


--
-- Name: codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.codes_id_seq', 20, true);


--
-- Name: credits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.credits_id_seq', 1, false);


--
-- Name: days_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.days_id_seq', 9, true);


--
-- Name: enrolls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enrolls_id_seq', 1, false);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 58, true);


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.feedback_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 3, true);


--
-- Name: top_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.top_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 8, true);


--
-- Name: vacations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vacations_id_seq', 1, false);


--
-- Name: classes classes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_pkey PRIMARY KEY (id);


--
-- Name: codes codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.codes
    ADD CONSTRAINT codes_pkey PRIMARY KEY (id);


--
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (id);


--
-- Name: days days_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.days
    ADD CONSTRAINT days_pkey PRIMARY KEY (id);


--
-- Name: enrolls enrolls_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrolls
    ADD CONSTRAINT enrolls_pkey PRIMARY KEY (id);


--
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- Name: feedback feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: top top_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_pkey PRIMARY KEY (id);


--
-- Name: users users_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_code_key UNIQUE (code);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vacations vacations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacations
    ADD CONSTRAINT vacations_pkey PRIMARY KEY (id);


--
-- Name: classes classes_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.classes
    ADD CONSTRAINT classes_id_fkey FOREIGN KEY (id) REFERENCES public.events(id);


--
-- Name: credits credits_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: credits credits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: enrolls enrolls_class_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrolls
    ADD CONSTRAINT enrolls_class_id_fkey FOREIGN KEY (class_id) REFERENCES public.classes(id);


--
-- Name: enrolls enrolls_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enrolls
    ADD CONSTRAINT enrolls_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: events events_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.days(id);


--
-- Name: feedback feedback_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- Name: feedback feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback
    ADD CONSTRAINT feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: top top_chosen_1_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_chosen_1_fkey FOREIGN KEY (chosen_1) REFERENCES public.users(id);


--
-- Name: top top_chosen_2_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_chosen_2_fkey FOREIGN KEY (chosen_2) REFERENCES public.users(id);


--
-- Name: top top_chosen_3_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_chosen_3_fkey FOREIGN KEY (chosen_3) REFERENCES public.users(id);


--
-- Name: top top_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.days(id);


--
-- Name: top top_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.top
    ADD CONSTRAINT top_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: vacations vacations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vacations
    ADD CONSTRAINT vacations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

