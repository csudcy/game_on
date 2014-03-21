/*
State dictionaries are something like this:
    var constant_info = {
        board: {
            width: ,
            height: ,
        }
        team_1: {
            player_count: ,
            max_health: ,
            effect_colour: , ('rgba(255, 0, 0, {alpha})')
            players: [
                {
                    id: ,
                    sight: ,
                    blast_radius: ,
                },
                ...
            ]
        },
        team_2: ...,
        projectile: {
            show_age: 5,
            fade_age: 15,
            max_age: 20,
        }
    }

    var tick_info = {
        team_1: {
            players: [
                {
                    x: ,
                    y: ,
                    direction: ,
                    turret_direction: ,
                    is_dead: ,
                    reload_frac: ,
                    target_x: ,
                    target_y: ,
                    target_r: ,
                    health: ,
                },
                ...
            ]
        },
        team_2: ...,
        projectiles: [
            {
                is_at_target: ,
                origin_x: ,
                origin_y: ,
                current_x: ,
                current_y: ,
                team: , (team_1, team_2)
                player: , (0-4)
                explosion_age: ,
            },
            ...
        ]
    };
*/

function draw_board(g, constant_info, tick_info) {
    /*Draw everything*/
    g.fillStyle = 'green';
    g.fillRect(0, 0, constant_info.board.width, constant_info.board.height);
    draw_team(g, constant_info.team_1, tick_info.team_1);
    draw_team(g, constant_info.team_2, tick_info.team_2);
    tick_info.projectiles.forEach(function(tick_info_projectile) {
        var constant_info_team = constant_info[tick_info_projectile.team],
            constant_info_player = constant_info_team.players[tick_info_projectile.player],
            constant_info_projectile = constant_info.projectile;
        draw_projectile(
            g,
            constant_info_team,
            constant_info_player,
            constant_info_projectile,
            tick_info_projectile
        );
    });
}

function draw_team(g, constant_info_team, tick_info_team) {
    /*Draw this team*/
    for (var i=0; i<constant_info_team.player_count; i++) {
        draw_player(
            g,
            constant_info_team,
            constant_info_team.players[i],
            tick_info_team.players[i]);
    }
}

function draw_player(g, constant_info_team, constant_info_player, tick_info_player) {
    /*Draw this player*/
    //Move to where we are
    g.save();
        g.translate(tick_info_player.x, tick_info_player.y);
        //Body
        g.save();
        g.rotate(tick_info_player.direction);
        g.beginPath();
        g.moveTo(-10, -15);
        g.lineTo( 25,   0);
        g.lineTo(-10,  15);
        g.closePath();
        g.strokeStyle = 'black';
        g.stroke();
        g.restore();
        //Turret
        g.save();
        g.rotate(tick_info_player.turret_direction);
        g.beginPath();
        g.moveTo(- 5, -5);
        g.lineTo( 15,  0);
        g.lineTo(- 5,  5);
        g.closePath();
        if (tick_info_player.is_dead) {
            g.fillStyle = 'grey';
        } else {
            g.fillStyle = 'rgba(255, 0, 0, ' + tick_info_player.reload_frac + ')';
        }
        g.fill();
        g.strokeStyle = 'red';
        g.stroke();
        g.restore();
        if (!tick_info_player.is_dead) {
            //Sight
            g.beginPath();
            g.arc(0, 0, constant_info_player.sight, 0, 2 * Math.PI, false);
            g.strokeStyle = 'white';
            g.stroke();
            g.closePath();
            //Health
            g.save();
            g.fillStyle = 'green';
            g.fillRect(-35, 25, 70, 10);
            g.fillStyle = 'white';
            g.fillRect(-35, 25, (tick_info_player.health / constant_info_team.max_health) * 70, 10);
            g.strokeStyle = 'black';
            g.strokeRect(-35, 25, 70, 10);
            g.restore();
        }
        //Central point
        g.fillStyle = 'white';
        g.fillRect(-1, -1, 2, 2);
        //Id
        g.fillStyle = constant_info_team.effect_colour.replace('{alpha}', '1.0');
        g.fillText(constant_info_player.id, 0, -20);
    g.restore();
    //Draw target
    if (!tick_info_player.is_dead && tick_info_player.target_r) {
        g.beginPath();
        g.arc(
            tick_info_player.target_x,
            tick_info_player.target_y,
            tick_info_player.target_r,
            0, 2 * Math.PI, false);
        g.strokeStyle = constant_info_team.effect_colour.replace('{alpha}', '1.0');
        g.stroke();
        g.closePath();
    }
}

function draw_projectile(
            g,
            constant_info_team,
            constant_info_player,
            constant_info_projectile,
            tick_info_projectile
        ) {
    if (!tick_info_projectile.is_at_target) {
        g.beginPath();
        g.moveTo(tick_info_projectile.origin_x, tick_info_projectile.origin_y);
        g.lineTo(tick_info_projectile.current_x, tick_info_projectile.current_y);
        g.strokeStyle = constant_info_team.effect_colour.replace('{alpha}', '1.0');
        g.stroke();
    } else {
        var r = constant_info_player.blast_radius,
            opacity = 0.7;
        if (tick_info_projectile.explosion_age < constant_info_projectile.show_age) {
            //Expand the explosion until we reach full size
            r *= tick_info_projectile.explosion_age / constant_info_projectile.show_age;
        } else if (tick_info_projectile.explosion_age > constant_info_projectile.fade_age) {
            //Fade the explosion until we reach max age
            opacity *= (constant_info_projectile.max_age - tick_info_projectile.explosion_age) /
                (constant_info_projectile.max_age - constant_info_projectile.fade_age);
        }
        g.beginPath();
        g.arc(
            tick_info_projectile.current_x,
            tick_info_projectile.current_y,
            r,
            0, 2 * Math.PI, false);
        g.fillStyle = constant_info_team.effect_colour.replace('{alpha}', opacity);
        g.fill();
    }
}
