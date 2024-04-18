-- free database
-- DROP TABLE IF EXISTS collection, picture, cropped_sign, sign;


-- use postgis to manipule geometries
CREATE EXTENSION IF NOT EXISTS postgis;


-- ------------------------------------------------------------------ --
-- --  Tables and constraints                                      -- --
-- ------------------------------------------------------------------ --

CREATE TABLE public.collection
(
	id CHARACTER VARYING(256) NOT NULL,
	"date" DATE NOT NULL,
	
	PRIMARY KEY (id)
);


ALTER TABLE IF EXISTS public.collection
	OWNER to postgres;


CREATE TABLE public.picture
(
	id CHARACTER VARYING(256) NOT NULL,
	collection_id CHARACTER VARYING(256) NOT NULL,
	geom GEOMETRY (POINT, 4326) NOT NULL,
	azimut FLOAT NOT NULL,
	width INTEGER NOT NULL,
	height INTEGER NOT NULL,
	fov FLOAT,
	model CHARACTER VARYING(256),

	PRIMARY KEY (id),
	FOREIGN KEY (collection_id)
		REFERENCES public.collection (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
);

ALTER TABLE IF EXISTS public.picture
	OWNER to postgres;


CREATE TABLE public.sign
(
	id SERIAL NOT NULL,
	geom GEOMETRY(POINT, 4326) NOT NULL,
	"size" FLOAT NOT NULL,
	orientation FLOAT NOT NULL, 
	precision FLOAT NOT NULL,
	code CHARACTER VARYING(16) NOT NULL,
	"value" CHARACTER VARYING(256) DEFAULT NULL,
	
	PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.sign
	OWNER to postgres;


CREATE TABLE public.cropped_sign
(
	id SERIAL NOT NULL,
	picture_id CHARACTER VARYING NOT NULL,
	sign_id INTEGER DEFAULT NULL,
	"filename" CHARACTER VARYING NOT NULL,
	x FLOAT,
	y FLOAT,
	dz FLOAT,		
	sdf FLOAT,		-- size_dist_factor: dist = size * sdf
	gisement FLOAT,		-- in degrees from North
	orientation FLOAT,	-- in degrees from North
	bbox CHARACTER VARYING,
	code CHARACTER VARYING(16) NOT NULL,
	"value" CHARACTER VARYING(256) DEFAULT NULL,
	
	PRIMARY KEY(id),
	FOREIGN KEY (picture_id)
		REFERENCES public.picture (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID,
	FOREIGN KEY (sign_id)
		REFERENCES public.sign (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
		NOT VALID
);

ALTER TABLE IF EXISTS public.cropped_sign
	OWNER to postgres;
