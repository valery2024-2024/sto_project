BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "alembic_version" VALUES('ed9d40639c40');
CREATE TABLE appointment (
	id INTEGER NOT NULL, 
	client_id INTEGER NOT NULL, 
	date VARCHAR(20), 
	time VARCHAR(20), 
	service VARCHAR(100), 
	comment TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(client_id) REFERENCES client (id)
);
CREATE TABLE booking (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	date VARCHAR(20) NOT NULL, 
	comment TEXT, 
	email VARCHAR(120) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "booking" VALUES(1,'Кирило','0961243202','2025-02-19','спустило колесо','kiril@gmail.com');
INSERT INTO "booking" VALUES(2,'Stepan','0961243202','2025-02-20','гуде переднє колесо','stepan@gmail.com');
INSERT INTO "booking" VALUES(3,'Богдан','0961243202','2025-02-20','Заклинив підшипник в генераторі','bogdan@gmail.com');
INSERT INTO "booking" VALUES(4,'Ярослав','0677335460','2025-02-20','не світить лампочка','yarik@gmail.com');
INSERT INTO "booking" VALUES(5,'Кирило','0961243202','2025-02-27','спустило колесо','kiril@gmail.com');
INSERT INTO "booking" VALUES(6,'Толік','+380670000001','2025-03-01','Толік перший','tolik@gmail.com');
INSERT INTO "booking" VALUES(7,'Толік','+380670000002','2025-03-01','Толік другий Луцьк','tolik@gmail.com');
INSERT INTO "booking" VALUES(8,'Толік','+380670000003','2025-03-01','Толік третій Славута','tolik@gmail.com');
INSERT INTO "booking" VALUES(9,'Толік','+380670000004','2025-03-01','Толік четвертий ОНЛАЙН ЗАПИС','tolik@gmail.com');
INSERT INTO "booking" VALUES(10,'Толік ','+380670000005','2025-03-01','Толік п''ятий ШИНОМОНТАЖ','tolik@gmail.com');
INSERT INTO "booking" VALUES(11,'Богдан','0961243202','2025-03-11','вапвапвапв','vadim@gmail.com');
INSERT INTO "booking" VALUES(12,'Владислав','+380933004050','2025-03-13','Перевірка коментар','vlaadislav@gmail.com');
INSERT INTO "booking" VALUES(13,'Кирило','+380670000003','2025-03-13','Другий коментар перевірка','kiril@gmail.com');
INSERT INTO "booking" VALUES(14,'Сергій','+380671010101','2025-03-31','Генератор перестав працювати','sergii@gmail.com');
INSERT INTO "booking" VALUES(15,'Сергій','+380671010101','2025-03-31','Замінити резину на літню','sergii@gmail.com');
INSERT INTO "booking" VALUES(16,'Мирослав','+380674045679','2025-04-21','Замінити зимову резину на літню.','miroslav@example.com');
INSERT INTO "booking" VALUES(17,'Мирослав','+380674045679','2025-04-22','Зробити стартер','miroslav@example.com');
INSERT INTO "booking" VALUES(18,'Мирослав','+380674045679','2025-04-22','Замінити генератор','miroslav@example.com');
CREATE TABLE "car" (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	engine INTEGER NOT NULL, 
	fuel_consumption FLOAT NOT NULL, 
	register BOOLEAN, 
	user_id INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT fk_car_user_id FOREIGN KEY(user_id) REFERENCES user (id)
);
INSERT INTO "car" VALUES(1,'Dacia',87,10.0,0,12);
INSERT INTO "car" VALUES(2,'BMW',100,12.0,1,12);
INSERT INTO "car" VALUES(3,'Ford',90,9.0,0,20);
INSERT INTO "car" VALUES(4,'Lincoln',220,19.0,1,5);
INSERT INTO "car" VALUES(5,'Tesla',300,0.0,1,23);
CREATE TABLE client (
	id INTEGER NOT NULL, 
	name VARCHAR(100), 
	phone VARCHAR(20), 
	email VARCHAR(100), 
	PRIMARY KEY (id)
);
CREATE TABLE contact_message (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	phone VARCHAR(20) NOT NULL, 
	message TEXT NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO "contact_message" VALUES(1,'mikola','0677335460','генератор не дає зарядку');
INSERT INTO "contact_message" VALUES(2,'Владислав','0671234567','гримить ходова');
INSERT INTO "contact_message" VALUES(3,'Толік','0670000006','Толік шостий ЗАЛИШТЕ ЗАЯВКУ');
INSERT INTO "contact_message" VALUES(4,'Толік','+380670000003','Толік ти все правильно зробив.');
INSERT INTO "contact_message" VALUES(5,'Богдан','0961243202','Богдан все правильно зробив');
INSERT INTO "contact_message" VALUES(6,'Вадим','+380670000001','Все зробили швидко та якісно. Мені сподобалось.');
INSERT INTO "contact_message" VALUES(7,'Сергій','+380671010101','Моє авто зробили швидко та оперетивно.');
CREATE TABLE message (
	id INTEGER NOT NULL, 
	name VARCHAR(100), 
	email VARCHAR(100), 
	message TEXT, 
	PRIMARY KEY (id)
);
CREATE TABLE user (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(120) NOT NULL, 
	password VARCHAR(200) NOT NULL, 
	is_admin BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
INSERT INTO "user" VALUES(1,'Admin','admin@example.com','pbkdf2:sha256:1000000$xdrpbsjZnFtpVV5u$1b981d9b1e9dc5d2b668d665e892144e014db7e98b41217676cccfd8a72dadd9',1);
INSERT INTO "user" VALUES(4,'Вадим','vadim@gmail.com','pbkdf2:sha256:1000000$CllmNQBz1LlWuSLW$e06df641d7b672e938b54ea6a2d6e44028610e35da92eca96d58918bd7a95d4e',0);
INSERT INTO "user" VALUES(5,'Max','max@gmail.com','pbkdf2:sha256:1000000$CZITF0FPr5OOS6oF$29df18be0ea97a44d96c77bc2deb6c43c11ad360a3b68523260a9f850a8a8b3a',0);
INSERT INTO "user" VALUES(6,'Yra','yra@gmail.com','pbkdf2:sha256:1000000$liL5n4qZ4lqHdUC8$0db1622b4c1e621cc45f286e20911df6de52c245794e09e54fde3c8bd0dbeadd',0);
INSERT INTO "user" VALUES(7,'Vladlen','vladlen@gmail.com','pbkdf2:sha256:1000000$JGqkPdX1LkxkdenA$b15010ab1c62692a326a02dc5014a9fe92f8b3148e1eeb32f28318b1756c0d10',0);
INSERT INTO "user" VALUES(8,'Roman','roman@gmail.com','pbkdf2:sha256:1000000$pRhRmyZOcCrdNoGF$80b651775518b2875a233e5fac12366426f7ca0bcf1801d1d105934174de6e1c',0);
INSERT INTO "user" VALUES(9,'Viktor','viktor@gmail.com','pbkdf2:sha256:1000000$eg6DSvcv9WAKNWFN$24fccd57569bbedc15abb21bdb9788fb56e9c8ae26ec4a5a338d503ca9ad0221',0);
INSERT INTO "user" VALUES(10,'romario','romario@gmail.com','pbkdf2:sha256:1000000$MWLbiAk7xrzrHfgF$c0bf31c73702585f31a2e594ffa839a0f9862c38d2b7dd67590503f917e51855',0);
INSERT INTO "user" VALUES(11,'Tanya','tanya@gmail.com','pbkdf2:sha256:1000000$IksC5NKDMj1mgA7J$e517a024fea09dc8084694a05f41c8be28fde5d149339a04ef314449d4e39a3a',0);
INSERT INTO "user" VALUES(12,'Толік','tolik@gmail.com','pbkdf2:sha256:1000000$iGSqiyddhkfMCbRg$36d32331db30a3f6ccd085911cf7fa76c5bcd22151ef2368bfb40273f8406ced',0);
INSERT INTO "user" VALUES(13,'Тролік','trolik@gmail.com','pbkdf2:sha256:1000000$SlRaJ1RiH2BzAryc$b554a8d023949dd59f5784b7c2298f4099f7b0e1895a0dbb178baf5e9ef931b9',0);
INSERT INTO "user" VALUES(14,'Тотолік','totolik@gmail.com','pbkdf2:sha256:1000000$iJKF7ARZMjC0T5J1$350b47c8ba172e6752dd63ded747143559c3c9d4be9129e3aac2bb8f746dc278',0);
INSERT INTO "user" VALUES(15,'Толік нова реєстрація','trolikk@gmail.com','pbkdf2:sha256:1000000$dzl310B4bryTXhxB$bfb31f86317a5bae0a7d6c283d2e626ee19faccacc955afec1e9d69a549f98b6',0);
INSERT INTO "user" VALUES(16,'Микола ПЕРША РЕЄСТРАЦІЯ','mikolas@gmail.com','pbkdf2:sha256:1000000$Lj8BQtdrFfSgi3Ew$480a999c13aa418d362c4254b902f169547badbc164e0864268546a8e182462c',0);
INSERT INTO "user" VALUES(17,'example','example@example.com','pbkdf2:sha256:1000000$8K4r9bBE9JukciQi$cc4c545c1baa78a16dd03959184ec27eae134308317c4894d399ac0f2dc29d7c',0);
INSERT INTO "user" VALUES(18,'Саша','sasha@gmail.com','pbkdf2:sha256:1000000$33IQ4aOhPpgWgfoc$b05f5bb3e08d57f505e73f98ab498fc97b3a0164b6ddd4b82b64e1d0900cd681',0);
INSERT INTO "user" VALUES(19,'Дмитро','dimasof2009@gmail.com','pbkdf2:sha256:1000000$OK74okVazK1Iymmq$eb1d5cbf86a75882783d2f032d9ab4090c23d355ed839adbe0e79740621023d3',0);
INSERT INTO "user" VALUES(20,'Равон','ravon@gmail.com','pbkdf2:sha256:1000000$dUvOfi1b793AkOKK$a050eb4752716d9b27fe65635b42de936d128f6771c6ac27a4ed2d8c81afc43a',0);
INSERT INTO "user" VALUES(21,'Равіолі','ravioli@gmail.com','pbkdf2:sha256:1000000$i4mhOQd9nHsGooVY$bc82868946c4a93b90110341b1f8cfdc2dfeac8d02489b4725a5b40f1e3e29a5',0);
INSERT INTO "user" VALUES(22,'Рівіан','rivian@gmail.com','pbkdf2:sha256:1000000$NDoncANsOmHgHAiL$0154e4fac616918d882ce7ba9f63afa436d36a7287613b1587c708871a7a3902',0);
INSERT INTO "user" VALUES(23,'Петро','petro@gmail.com','pbkdf2:sha256:1000000$EFHLpAnXMudueWyq$7cc0b40fc166dc3b7dcd033ee0c4d76f5908851fc6a3e38d33d88b776bcf31a6',0);
INSERT INTO "user" VALUES(24,'Марк','mark@gmail.com','pbkdf2:sha256:1000000$0rUJ4ZGoJNnjFp70$6aed9795d1357f65773241fb026ee42f4feccfe025470b2f2dcee963b8b99190',0);
INSERT INTO "user" VALUES(25,'Антон','anton@gmail.com','pbkdf2:sha256:1000000$0tNGEes9vQnHng36$00fee237b167c11c4093497a0ecc1b40f6f5f212474819956a3c047aa7b1aeb7',0);
INSERT INTO "user" VALUES(26,'Сергій','sergii@gmail.com','pbkdf2:sha256:1000000$jDXIMZfMsxHfr4Tq$cd892f412271e4f8052f01c7b2502dcea1b2875d366572ba11e6a63ada612a7b',0);
INSERT INTO "user" VALUES(27,'Мирослав','miroslav@example.com','pbkdf2:sha256:1000000$NDzUdrVmJXEg8wah$fde8b9d9a62c2168fff54ead9b40d9fb14899845bcffc102bbe7956c5b856da0',0);
COMMIT;
