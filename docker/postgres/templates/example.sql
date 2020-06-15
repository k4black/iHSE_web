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
    validator_id integer,
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
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer,
    token text
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


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
    time_to text DEFAULT ''::text,
    accepted boolean DEFAULT false
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
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


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
11	10	
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
59	0	
60	0	
61	0	
62	0	
63	0	
65	0	
66	0	
67	0	
68	0	
69	0	
70	0	
72	0	
73	0	
74	0	
78	0	
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
7	Q920N6	0	t
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

COPY public.credits (id, user_id, event_id, validator_id, "time", value) FROM stdin;
2	5	11	0	2020-06-02 09:46:30 MSK	15
1	4	11	0	2020-06-02 13:42:30 MSK	10
3	8	11	24	2020-06-02 13:42:30 MSK	10
4	7	11	23	2020-06-02 11:16:31 MSK	10
5	13	11	0	2020-06-02 13:42:30 MSK	12
6	14	11	0	2020-06-02 11:16:31 MSK	10
7	5	12	23	2020-06-02 11:16:31 MSK	5
8	1	5	23	2020-06-02 11:16:31 MSK	3
9	5	21	23	2020-06-02 11:16:31 MSK	10
10	4	21	23	2020-06-02 11:16:31 MSK	10
12	7	21	24	2020-06-02 11:16:31 MSK	12
13	11	21	24	2020-06-02 11:16:31 MSK	10
14	6	21	24	2020-06-02 11:16:31 MSK	10
16	1	21	0	2020-06-02 13:42:30 MSK	12
\.


--
-- Data for Name: days; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.days (id, date, title, feedback) FROM stdin;
0	NO DAY		f
1	05.06		t
4	08.06		f
5	09.06		f
7	11.06		f
3	07.06		t
6	10.06		t
8	12.06		f
9	13.06		t
2	06.06		t
\.


--
-- Data for Name: enrolls; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.enrolls (id, class_id, user_id, "time", attendance, bonus) FROM stdin;
1	11	2	2020-06-02 13:46:30 MSK	f	0
2	11	4	2020-06-02 11:16:30 MSK	t	0
3	11	5	2020-06-02 09:46:30 MSK	t	5
4	11	8	2020-06-02 13:42:30 MSK	t	0
5	11	7	2020-06-02 11:16:31 MSK	t	0
6	11	15	2020-06-02 13:42:30 MSK	f	2
7	11	13	2020-06-02 13:42:30 MSK	t	2
8	11	14	2020-06-02 11:16:31 MSK	t	0
9	21	5	2020-06-02 11:16:31 MSK	t	0
10	21	4	2020-06-02 11:16:31 MSK	t	0
12	21	7	2020-06-02 11:16:31 MSK	t	2
13	21	11	2020-06-02 11:16:31 MSK	t	0
14	21	15	2020-06-02 11:16:31 MSK	f	0
15	21	13	2020-06-02 11:16:31 MSK	f	0
16	21	6	2020-06-02 11:16:31 MSK	t	0
17	21	1	2020-06-02 11:16:31 MSK	t	2
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
10	0	Ужин				19.00\n19.30	1
13	2	Легенда лагеря – Школьный университет «iВышка»		А.А. Бляхман, Н.А. Серова	КЛУБ	20.10\n21.00	1
14	0	Кефир				21.00\n21.10	1
16	0	Рефлексия				22.20\n22.45	1
17	0	Отбой				23.00	1
15	3	Спевка		Вожатые	ЗАЛ (столовая)	21.10\n22.10	1
12	3	Подготовка к концерту «Таланты iВышки»			Отрядные комнаты	19.30\n20.00	1
9	3	Подготовка к концерту «Таланты iВышки»		Все участники смены	Отрядные комнаты	17.30\n19.00	1
5	3	Верёвочный курс		Вожатые	Линейка	14.00\n16.00	1
1	3	Регистрация отъежающих в лагерь	Фотографирование		НИУ ВШЭ, Большая Печерская, 25/12	8.30\n10.00	1
19	0	Сбор отрядов			Линейка	8.50	2
20	0	Завтрак				9.00\n10.00	2
21	2	Всё о проектах	Проектная работа: установочная сессия	Екатерина Прохорова	ЗАЛ (столовая)	10.00\n11.20	2
24	2	Всё о проектах	Проектная работа: установочная сессия	Екатерина Прохорова	ЗАЛ (столовая)	11.30\n12.50	2
26	0	Баня // Отдых				13.30\n14.30	2
25	0	Обед				13.00\n14.00	2
27	1	"Опять об Пушкине!"	Пушкин как литературный герой	М.М. Гельфонд	ЗАЛ (столовая)	14.30\n16.00	2
31	0	Полдник				16.00\n16.10	2
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
45	1	Цифровая экономика или почему роботы будут завидовать экономистам?		М.А. Штефан	ЗАЛ (столовая)	14.30\n15.50	3
46	0	Полдник				16.00\n16.10	3
51	1	"Танцуем Вальс"	Занятие 1-6\n(обязательное посещение всех шести занятий)	Михаил Кортунов	КЛУБ	16.10\n17.30	3
52	3	Подготовка к вечернему концерту «Таланты iВышки»			Клуб, отрядные комнаты	17.30\n19.00	3
54	0	Ужин				19.00\n19.30	3
11	1	Танцуй, iВышка!		Лада Зотова	Танц. площадка	19.30\n20.00	1
22	2	iВышка - участник  "Проект 800"	О содержании проектной и исследовательской деятельности	Милана Евстигнеева	КЛУБ	10.00\n11.20	2
23	2	iВышка - участник  "Проект 800"	О содержании проектной и исследовательской деятельности	Милана Евстигнеева	КЛУБ	11.30\n12.50	2
28	1	Все врут	или что в действительности нужно клиентам вашего бизнеса	Д.В. Сидоров	КЛУБ	14.30\n16.00	2
29	2	Исследование & проект: в чем отличие?	Исследовательская работа: установочная сессия	Милана Евстигнеева	Комп. класс 1	14.30\n16.00	2
30	1	Проектирование досуговых мероприятий в лагере		Ксения Бурлак	Дача 3, подъезд 2	14.30\n16.00	2
44	1	Школа французского для начинающих	Заняти 1-4	Елизавета Капелева	Комп. класс 1	14.30\n15.50	3
43	1	Программирование без компьютеров	Занятие 1-1	Ирина Саблина	Корпус Хабенских, 2 этаж	14.30\n15.50	3
42	1	iМедиа & iNews	Занятие 1-6	Мариам Мкртумян, Анастасия Кирсанова	Большая стекляшка	14.30\n15.50	3
47	1	Школа немецкого	Занятие 1-3	Ирина Мартышкина	Дача 3, подъезд 2	16.10\n17.30	3
48	1	Итоговое сочинение: советы успешного абитуриента	Занятие 1-2	Яна Логинова	Большая стекляшка	16.10\n17.30	3
49	1	Уличный театр: кручение "пои"	Занятие 1-3	Константин Чернышев	Танц. площадка	16.10\n17.30	3
50	1	Математика: 19 задание ЕГЭ летом	Заняти 1-3	Михаил Кузнецов	Комп. класс 1	16.10\n17.30	3
53	1	Бейсбол		Никита Власюк	Фут. поле	17.30\n19.00	3
55	3	Подготовка к вечернему концерту «Таланты iВышки»				19.30\n20.00	3
56	3	Концерт «Таланты iВышки»	Перерыв (Кефир): 21.00 – 21.10		КЛУБ	20.15\n22.00	3
57	0	Рефлексия				22.20\n22.45	3
58	0	Отбой				23.00	3
18	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	2
61	1	Секреты успешной команды	Формируем проектную /исследовательскую команду	Елизавета Бессчетнова	Большая стекляшка	16.20\n17.00	2
62	1	Как рождаются новые идеи?	Проектный инструментарий	Милана Евстигнеева	Комп. класс 1	16.20\n17.00	2
63	1	Направление "Туризм"	Поиск идеи будущего проекта / исследования	Никита Власюк	Дача 1, подъезд 1	16.20\n17.00	2
65	1	Направление "Событийная программа"	Поиск идеи будущего проекта / исследования	Анна Берсенина, Евгений Журавлёв	Корпус Хабенских, 2 этаж	17.10\n17.50	2
66	1	Направление "Цифровые технологии"	Поиск идеи будущего проекта / исследования	М.В. Рамина, Константин Чернышев, Ирина Саблина	Комп. класс 2	17.10\n17.50	2
67	1	Направление "Медиапроекты, кино"\t	Поиск идеи будущего проекта / исследования	Мариам Мкртумян, Анастасия Кирсанова	КЛУБ	17.10\n17.50	2
68	1	Направление "Просвещение"	Поиск идеи будущего проекта / исследования	Яна Логинова, Н.А. Серова	Дача 3, подъезд 2	18.00\n18.40	2
69	1	Секреты успешной команды	Формируем проектную /исследовательскую команду	Елизавета Бессчетнова	Большая стекляшка	18.00\n18.40	2
70	1	Направление "Цифровые технологии"	Поиск идеи будущего проекта / исследования	М.В. Рамина, Константин Чернышев, Ирина Саблина	Комп. класс 2	18.00\n18.40	2
72	1	Направление "Медиапроекты, кино"\t	Поиск идеи будущего проекта / исследования	Мариам Мкртумян, Анастасия Кирсанова	КЛУБ	18.00\n18.40	2
73	1	Направление "Туризм"	Поиск идеи будущего проекта / исследования	Никита Власюк	Дача 1, подъезд 1	18.00\n18.40	2
74	1	Как рождаются новые идеи?	Проектный инструментарий	Милана Евстигнеева	Комп. класс 1	17.10\n17.50	2
75	0	Ужин				19.00\n19.30	2
76	3	Презентация и выбор досуговых мероприятий лагеря		Группа проектировщиков досуга	ЗАЛ (столовая)	19.30\n21.00	2
77	0	Кефир				21.00\n21.10	2
79	3	Самозапись проектной деятельности	проектная / иследовательская группа + направление + идея\t\t\t\t	Все	Сайт	22.10\n22.15	2
81	0	Отбой				23.00	2
80	0	Рефлексия				22.20\n22.45	2
78	1	Танцуй, iВышка!		Лада Зотова	Танц. площадка	21.10\n22.10	2
86	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	4
87	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	5
88	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	6
89	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	7
90	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	8
91	0	Подъем, зарядка, умывание, порядок в комнате				8.00\n8.50	9
92	0	Сбор отрядов			Линейка	8.50	4
93	0	Сбор отрядов			Линейка	8.50	5
94	0	Сбор отрядов			Линейка	8.50	6
95	0	Сбор отрядов			Линейка	8.50	7
96	0	Сбор отрядов			Линейка	8.50	8
97	0	Сбор отрядов			Линейка	8.50	9
98	0	Завтрак				9.00\n10.00	4
99	0	Завтрак				9.00\n10.00	5
100	0	Завтрак				9.00\n10.00	6
101	0	Завтрак				9.00\n10.00	7
102	0	Завтрак				9.00\n10.00	8
103	0	Завтрак				9.00\n10.00	9
104	0	Обед				13.00\n14.00	4
105	0	Обед				13.00\n14.00	5
106	0	Обед				13.00\n14.00	6
107	0	Обед				13.00\n14.00	7
108	0	Обед				13.00\n14.00	8
109	0	Обед				13.00\n14.00	9
110	0	Баня // Отдых				13.30\n14.30	4
111	0	Баня // Отдых				13.30\n14.30	5
112	0	Баня // Отдых				13.30\n14.30	6
113	0	Баня // Отдых				13.30\n14.30	7
114	0	Баня // Отдых				13.30\n14.30	8
115	0	Баня // Отдых				13.30\n14.30	9
116	0	Ужин				19.00\n19.30	4
117	0	Ужин				19.00\n19.30	5
118	0	Ужин				19.00\n19.30	6
119	0	Ужин				19.00\n19.30	7
120	0	Ужин				19.00\n19.30	8
121	0	Ужин				19.00\n19.30	9
122	0	Рефлексия				22.20\n22.45	4
123	0	Рефлексия				22.20\n22.45	5
124	0	Рефлексия				22.20\n22.45	6
125	0	Рефлексия				22.20\n22.45	7
126	0	Рефлексия				22.20\n22.45	8
127	0	Рефлексия				22.20\n22.45	9
128	0	Отбой				23.00	4
129	0	Отбой				23.00	5
130	0	Отбой				23.00	6
131	0	Отбой				23.00	7
132	0	Отбой				23.00	8
133	0	Отбой				23.00	9
134	0	Полдник				16.00\n16.10	4
135	0	Полдник				16.00\n16.10	5
136	0	Полдник				16.00\n16.10	6
137	0	Полдник				16.00\n16.10	7
138	0	Полдник				16.00\n16.10	8
139	0	Полдник				16.00\n16.10	9
8	1	Проектирование досуговых мероприятий в лагере		Ксения Бурлак	Дача 3, подъезд 2	17.30\n19.00	1
59	1	Направление "Просвещение"	Поиск идеи будущего проекта / исследования	Яна Логинова, Н.А. Серова	Дача 3, подъезд 2	16.20\n17.00	2
60	1	Направление "Событийная программа"	Поиск идеи будущего проекта / исследования	Анна Берсенина, Евгений Журавлёв	Корпус Хабенских, 2 этаж	16.20\n17.00	2
\.


--
-- Data for Name: feedback; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.feedback (id, user_id, event_id, score, entertain, useful, understand, comment) FROM stdin;
1	2	11	8	5	8	8	
2	4	11	6	8	5	4	
3	5	11	9	10	10	2	Нихрена не понятно, но очень интересно
4	8	11	6	8	4	10	
5	7	11	3	10	6	5	Норм
6	14	11	9	9	9	9	9
7	5	21	6	7	6	4	Проекты - дноооо
8	4	21	9	4	5	6	А может и норм, но нужно думать над темой. Дааа, это тяжело, - шевелить мозгами.
9	7	21	6	9	1	1	
10	11	21	5	7	6	2	
11	6	21	8	9	2	4	
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notifications (id, user_id, token) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, title, type, def_type, direction, description, annotation) FROM stdin;
0	NO PROJECT					
1	Умные остановки	project	presentation	media	Описание проекта умных остановок, который довольно большой. Тут должны описываться общие этапы.	Делаем умные остановки для нижнего
2	Цифровой Нижний	science	TED	IT	Модульная система обеспечивающая связь между администрацией и жителями Нижнего Новгорода.	Связь между администрацией и жителями.
3	Неформальный Нижний Новгород	other	TED	tourism	Этот проект будет посвящен местам в Нижнем Новгороде, о которых вы не задумывались ранее, но которые будут интересны всем вам. 	Путеводитель по Нижнему.
4	Умные Дети	project	presentation	education	Проект представляет собой непрерывное и старательно произсодство умных детей. Долгими ночами и долгими днями.	Тупому городу - Умные дети
5	Отчисление из ВыШЭ	science	TED	events	Лекция посвященная сложностям и проблемами с которыми столкнулся автор при отчислении из ВШЭ и последующей попытки суицида.	Доступное образование для всех!
7	iHSE	project	TED	IT	Официальный сайт летнего многопрофильного лагеря iВышка с расписанием, заческой, записью на мероприятия и отзывами.	Официальный сайт iВышки!
8	Шашлык-life	science	TED	events	Исследование непосредственного влияния проведения массовых мероприятий в Москве на политический климат.	Исследуем Шашлык-life!
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
\\x7714af63a0139e13b24e6b30d25f73c5	0	2	Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1	172.18.0.1	2020-06-05 19:47:34 MSK
\\x5295343c1aab4611f5887a0a31c9121d	0	2	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36	172.18.0.1	2020-06-05 19:48:07 MSK
\.


--
-- Data for Name: top; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.top (id, user_id, day_id, chosen_1, chosen_2, chosen_3) FROM stdin;
1	1	1	2	13	5
2	2	1	6	2	8
3	3	1	12	15	2
4	4	1	7	11	9
5	6	1	1	8	2
6	7	1	13	7	5
7	9	1	1	13	3
8	10	1	4	6	13
9	11	1	6	3	6
10	12	1	6	8	5
11	15	1	9	1	2
12	17	1	1	21	9
13	18	1	1	2	15
14	19	1	20	1	13
15	21	1	16	2	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, code, user_type, phone, name, sex, pass, team, project_id, avatar) FROM stdin;
0	NOCODE	2	72345678900	Automatic System	t	105934	0	0	https://icons.iconarchive.com/icons/diversity-avatars/avatars/1024/robot-01-icon.png
23	M1CODE	1	72345678901	Moderator First	t	105934	0	0	
24	M2CODE	1	72345678902	Moderator Second	f	105934	0	0	
2	Q920M7	0	79874289399	Игорь Прокопенко	t	105934	1	0	
12	18RGL4	0	79984772668	Иннокентий Мотыльков	t	105934	1	4	
13	64RTD4	0	79984772669	Жанна Абрамова	f	105934	1	0	
10	TTW7H9	0	79984772666	Игнатий Макридинов	t	105934	1	8	
11	HYW7Y9	0	79984772667	Ольга Поликова	f	105934	1	0	
9	TYR3H9	0	79984772665	Максим Варганов	t	105934	1	1	
6	F7Q6T4	0	79353522345	Максим Чернявский	t	105934	1	0	
3	1857L4	0	79441231233	Василина Петровна	f	105934	2	2	
8	TYW7Y4	0	79984772664	Анастасия Кревенко	f	105934	2	2	
15	05RGL4	0	79984772678	Дарья Чернигова	f	105934	2	1	
14	Q920M4	0	79984772677	Галина Залетская	f	105934	2	7	
5	MPJ840	0	79776664529	Оксана Антипова	f	105934	2	1	
18	05RGL7	0	79984772612	Никита Богданович	t	105934	2	0	
19	067GL8	0	79984772613	Константин Половский	t	105934	2	8	
20	058GL9	0	79984772614	Диана Яушева	f	105934	3	0	
21	058G10	0	79984772615	София Милешко	f	105934	3	0	
7	SOG6Q4	0	79266784848	Александр Никифоров	t	105934	3	3	
16	02RGL4	0	79984772679	Влад Мушкин	t	105934	3	1	
22	03RGL5	0	79984772610	Ольга Хиритонова	f	105934	3	0	
17	04RGL6	0	79984772611	Фёдор Витальевич	t	105934	3	0	
4	VW4946	0	79645266448	Евгения Зитцева	t	105934	3	2	
1	Y2G41J	0	79157043031	Юлия Самойлова	f	105934	3	5	
\.


--
-- Data for Name: vacations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.vacations (id, user_id, date_from, date_to, time_from, time_to, accepted) FROM stdin;
1	23	08.06	12.06	12.00	13.00	t
2	1	06.06	10.06	9.30	8.00	t
3	5	08.06	12.06	10.15	21.10	f
4	12	11.06	11.06	8.00	22.00	t
5	20	12.06	13.06	6.00	19.00	f
6	23	12.06	13.06	21.00	9.00	t
7	8	06.06	11.06	16.00	11.00	f
8	1	10.06	14.06	21.00	19.00	t
\.


--
-- Name: codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.codes_id_seq', 20, true);


--
-- Name: credits_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.credits_id_seq', 16, true);


--
-- Name: days_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.days_id_seq', 9, true);


--
-- Name: enrolls_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enrolls_id_seq', 17, true);


--
-- Name: events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.events_id_seq', 139, true);


--
-- Name: feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.feedback_id_seq', 11, true);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: projects_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.projects_id_seq', 8, true);


--
-- Name: top_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.top_id_seq', 15, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 25, true);


--
-- Name: vacations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.vacations_id_seq', 9, false);


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
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


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
-- Name: credits credits_validator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_validator_id_fkey FOREIGN KEY (validator_id) REFERENCES public.users(id);


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
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
    
    
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

