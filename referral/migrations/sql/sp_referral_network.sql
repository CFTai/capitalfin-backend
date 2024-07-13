DROP PROCEDURE IF EXISTS sp_referral_network;
DROP TABLE IF EXISTS referral_network;

CREATE PROCEDURE sp_referral_network(p_user_id INT)
BEGIN
	DROP TABLE IF EXISTS referral_network;
    
	-- CREATE temporary table for store result
	CREATE TEMPORARY TABLE referral_network(
		user_id INT, 
		username VARCHAR(150),
        first_name VARCHAR(150),
        last_name VARCHAR(150),
		referrer_id INT,
        referrer_username VARCHAR(150),
        lvl INT,
        network VARCHAR(225),
        network_type INT,
        PRIMARY KEY (user_id)
	);
    
    -- DOWN LINE NETWORK
    -- Run recursive CTE (query) and then insert into temporary table
	INSERT INTO referral_network
    (user_id, username, first_name, last_name, referrer_id, referrer_username, lvl, network, network_type)
	WITH RECURSIVE view_referral_network
	AS
	(
		SELECT
			a.id user_id, 
            a.username, 
            a.last_name, 
            a.first_name,
			b.referrer_id, 
            c.username referrer_username,  
			1 lvl, 
            a.username as network,
            1
		FROM
			user AS a
		LEFT OUTER JOIN
			referral AS b ON b.referred_id = a.id
		INNER JOIN
			user AS c ON b.referrer_id = c.id
		WHERE
			-- user procedure parameter user to fetch network
			a.is_staff = 0 AND CASE WHEN p_user_id IS NULL THEN b.referrer_id IS NULL ELSE b.referrer_id = p_user_id END
		
		UNION ALL
		
		SELECT
			a.id user_id, 
            a.username, 
            a.last_name, 
            a.first_name,
			b.referrer_id, 
            c.username referrer_username,  
			z.lvl + 1, 
            -- CONCAT(z.network, ' > ', a.username),
            z.network,
            1
		FROM
			view_referral_network AS z
		INNER JOIN
			referral AS b ON b.referrer_id = z.user_id
		INNER JOIN
			user AS c ON b.referrer_id = c.id
		INNER JOIN
			user AS a ON a.id = b.referred_id
	)
	SELECT * FROM view_referral_network;

	-- UP LINE NETWORK
    -- Run recursive CTE (query) and then insert into temporary table
	INSERT INTO referral_network
    (user_id, username, first_name, last_name, referrer_id, referrer_username, lvl, network, network_type)    
	WITH RECURSIVE view_referral_network
	AS
	(
		SELECT
			a.id user_id, 
            a.username, 
            a.last_name, 
            a.first_name,
			b.referrer_id, 
            c.username referrer_username,  
			1 lvl, 
            a.username as network,
            2
		FROM
			user AS a
		LEFT OUTER JOIN
			referral AS b ON b.referrer_id = a.id
		INNER JOIN
			user AS c ON b.referrer_id = c.id            
		WHERE
			-- user procedure parameter user to fetch network
			a.is_staff = 0 AND CASE WHEN p_user_id IS NULL THEN b.referred_id IS NULL ELSE b.referred_id = p_user_id END
            
		UNION ALL
		
		SELECT
			a.id user_id, 
            a.username, 
            a.last_name, 
            a.first_name,
			b.referrer_id, 
            c.username referrer_username,  
			z.lvl + 1, 
            -- CONCAT(z.network, ' < ', a.username),
            z.network,
            2
		FROM
			view_referral_network AS z
		INNER JOIN
			referral AS b ON b.referred_id = z.user_id
		INNER JOIN
			user AS c ON c.id = b.referred_id
		INNER JOIN
			user AS a ON a.id = b.referrer_id
	)
	SELECT * FROM view_referral_network;    

END