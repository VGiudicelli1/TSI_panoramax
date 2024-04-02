-- free database
-- DROP TABLE IF EXISTS sequence, photo, imagette, panneau;


-- use postgis to manipule geometries
CREATE EXTENSION IF NOT EXISTS postgis;


-- ------------------------------------------------------------------ --
-- --  Tables and constraints                                      -- --
-- ------------------------------------------------------------------ --

CREATE TABLE public.sequence
(
	id CHARACTER VARYING(256) NOT NULL,
	"date" DATE NOT NULL,
	
	PRIMARY KEY (id)
);


ALTER TABLE public.sequence
	OWNER to postgres;


CREATE TABLE public.photo
(
	id CHARACTER VARYING(256) NOT NULL,
	id_sequence CHARACTER VARYING(256) NOT NULL,
	geom GEOMETRY (POINT, 4326) NOT NULL,
	azimut FLOAT NOT NULL,
	width INTEGER NOT NULL,
	height INTEGER NOT NULL,
	
	PRIMARY KEY (id),
	FOREIGN KEY (id_sequence)
		REFERENCES public.sequence (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
);

ALTER TABLE public.photo
	OWNER to postgres;


CREATE TABLE public.panneau
(
	id SERIAL NOT NULL,
	geom GEOMETRY(POINT, 4326) NOT NULL,
	"size" FLOAT NOT NULL,
	orientation FLOAT NOT NULL, 
	precision FLOAT NOT NULL,
	
	PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.panneau
	OWNER to postgres;


CREATE TABLE public.imagette
(
	id CHARACTER VARYING(256) NOT NULL,
	id_photo CHARACTER VARYING NOT NULL,
	id_panneau INTEGER DEFAULT NULL,
	x FLOAT NOT NULL,
	y FLOAT NOT NULL,
	dz FLOAT NOT NULL,
	
	PRIMARY KEY(id),
	FOREIGN KEY (id_photo)
		REFERENCES public.photo (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID,
	FOREIGN KEY (id_panneau)
		REFERENCES public.panneau (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
);

ALTER TABLE IF EXISTS public.imagette
	OWNER to postgres;

