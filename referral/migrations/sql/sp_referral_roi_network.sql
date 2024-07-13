DROP PROCEDURE IF EXISTS sp_referral_roi_network;
DROP TABLE IF EXISTS referral_roi_network;

CREATE PROCEDURE sp_referral_roi_network(p_user_id INT)
BEGIN
	DROP TABLE IF EXISTS referral_roi_network;
    
	-- CREATE temporary table for store result
	CREATE TEMPORARY TABLE referral_roi_network(
		id INT AUTO_INCREMENT,
		user_id INT, 
		referrer_id INT,
        referrer_username VARCHAR(150),
        lvl INT,
        network VARCHAR(225),
        network_type INT,
        invest_bonus DOUBLE,
        PRIMARY KEY (id)
	);
    
    -- DOWN LINE NETWORK
    -- Run recursive CTE (query) and then insert into temporary table
	INSERT INTO referral_roi_network
    (user_id, referrer_id, referrer_username, lvl, network, network_type, invest_bonus)
	WITH RECURSIVE view_referral_roi_network
	AS
	(
		SELECT
			a.id user_id, 
			b.referrer_id, 
            c.username referrer_username,  
			1 lvl, 
            a.username as network,
            1,
            IFNULL(d.bonus, 0)
		FROM
			user AS a
		LEFT OUTER JOIN
			referral AS b ON b.referred_id = a.id
		INNER JOIN
			user AS c ON b.referrer_id = c.id
		LEFT OUTER JOIN
			stake AS e ON e.user_id = a.id
		LEFT OUTER JOIN
			invest AS f ON f.stake_id = e.id
		LEFT OUTER JOIN
			invest_bonus_transaction AS d ON d.invest_id = f.id AND d.status = 4
		WHERE
			-- user procedure parameter user to fetch network
			a.is_staff = 0 AND CASE WHEN p_user_id IS NULL THEN b.referrer_id IS NULL ELSE b.referrer_id = p_user_id END
		
		UNION ALL
		
		SELECT
			a.id user_id, 
			b.referrer_id, 
            c.username referrer_username,  
			z.lvl + 1, 
            -- CONCAT(z.network, ' > ', a.username),
            z.network,
            1,
			IFNULL(d.bonus, 0)
		FROM
			view_referral_roi_network AS z
		INNER JOIN
			referral AS b ON b.referrer_id = z.user_id
		INNER JOIN
			user AS c ON b.referrer_id = c.id
		INNER JOIN
			user AS a ON a.id = b.referred_id
		LEFT OUTER JOIN
			stake AS e ON e.user_id = a.id
		LEFT OUTER JOIN
			invest AS f ON f.stake_id = e.id
		LEFT OUTER JOIN
			invest_bonus_transaction AS d ON d.invest_id = f.id AND d.status = 4
	)
	SELECT * FROM view_referral_roi_network;

END