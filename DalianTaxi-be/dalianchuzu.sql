CREATE DATABASE dalianchuzu OWNER postgres;
GRANT ALL PRIVILEGES ON DATABASE dalianchuzu to postgres;

\c dalianchuzu
CREATE TABLE users(
    id SERIAL NOT NULL,
    phone VARCHAR(30) NOT NULL,
    password VARCHAR(64) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    is_driver BOOLEAN NOT NULL default false,
    register_time timestamp default now(),

  CONSTRAINT PK_id PRIMARY KEY (id),
  CONSTRAINT UQ_phone UNIQUE (phone)
);

CREATE TABLE orders (
  id              SERIAL           NOT NULL,
  start_time      TIMESTAMP        NOT NULL, -- 出行时间
  end_time        TIMESTAMP        NOT NULL, -- 失效时间
  launch_user_id  INT              NOT NULL,
  take_user_id    INT              DEFAULT NULL,
  description     VARCHAR(150)     NOT NULL, -- 备注
  start_address   VARCHAR(70)      NOT NULL, -- 起始位置
  end_address     VARCHAR(70)      NOT NULL, -- 终止位置
  state           INT              NOT NULL, --状态

  CONSTRAINT PK_id_orders PRIMARY KEY (id),
  CONSTRAINT FK_launch_user_id FOREIGN KEY (launch_user_id) REFERENCES users(id),
  CONSTRAINT FK_take_user_id FOREIGN KEY (take_user_id) REFERENCES users(id)
);