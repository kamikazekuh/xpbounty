from config.manager import ConfigManager
from wcs import wcsgroup
import wcs
from events import Event
from players.entity import Player
from filters.players import PlayerIter


cfg = ConfigManager('xpbounty')
streakvar = cfg.cvar("wcs_xpbounty_cfg_streak",5)
teambountyvar = cfg.cvar("wcs_xpbounty_cfg_team_bounty",0)
telltypevar = cfg.cvar("wcs_xpbounty_cfg_tell_type",0)
xpstartvar = cfg.cvar("wcs_xpbounty_cfg_xp_start",5)
xpincreasevar = cfg.cvar("wcs_xpbounty_cfg_xp_increase",5)
cfg.write()

streak = streakvar.get_int()
teambounty = teambountyvar.get_int()
telltype = telltypevar.get_int()
xpstart = xpstartvar.get_int()
xpincrease = xpincreasevar.get_int()


@Event('player_activate')
def player_activate(ev):
	wcsgroup.setUser(ev["userid"],"wcs_bounty_kills",0)
	wcsgroup.setUser(ev["userid"],"wcs_bounty_bounty",0)

	
@Event('player_death')
def player_death(ev):
	atk_play = Player.from_userid(ev['attacker'])
	vic_play = Player.from_userid(ev['userid'])
	if vic_play.userid == atk_play.userid or not atk_play.userid or not teambounty and vic_play.team == atk_play.team:
		return
	kills = int(wcsgroup.getUser(atk_play.userid,"wcs_bounty_kills")) + 1
	wcsgroup.setUser(atk_play.userid,"wcs_bounty_kills",kills)
	bounty = int(wcsgroup.getUser(atk_play.userid,"wcs_bounty_bounty"))
	if kills == int(streak):
		wcsgroup.setUser(atk_play.userid,"wcs_bounty_bounty",int(xpstart))
		if int(telltype):
			wcs.wcs.tell(atk_play.userid,"\x04[WCS]\x05 You started a bounty of \x04%s\x05."%xpstart)
		else:
			for player in PlayerIter():
				wcs.wcs.tell(player.userid,"\x04[WCS]\x05 Player \x04%s \x05has started a bounty of \x04%s\x05."%(atk_play.name,xpstart))
	elif kills > int(streak):
		bounty += int(xpincrease)
		wcsgroup.setUser(atk_play.userid,"wcs_bounty_bounty",bounty)
		if int(telltype):
			wcs.wcs.tell(atk_play.userid,"\x04[WCS]\x05 Your bounty increased to \x04%s\x05."%bounty)
		else:
			for player in PlayerIter():
				wcs.wcs.tell(player.userid,"\x04[WCS]\x05Player \x04%s \x05bounty has increased to \x04%s\x05."%(atk_play.name,bounty))
	bounty = int(wcsgroup.getUser(ev["userid"],"wcs_bounty_bounty"))
	kills = int(wcsgroup.getUser(ev["userid"],"wcs_bounty_kills"))
	if bounty and kills:
		wcs.wcs.getPlayer(atk_play.userid).giveXp(bounty,"bounty experience")
		if int(telltype):
			wcs.wcs.tell(atk_play.userid,"\x04[WCS]\x05 You stole \x05%s bounty of \x04%s\x05."%(vic_play.name,bounty))
			wcs.wcs.tell(vic_play.userid,"\x04[WCS]\x05 \x04%s \x05stole your bounty of \x04%s\x05."%(atk_play.name,bounty))
		else:
			for player in PlayerIter():
				wcs.wcs.tell(player.userid,"\x04[WCS]\x05 Player \x04%s\x05 has stolen \x04%s\x05 bounty of \x04%s\x05."%(atk_play.name,vic_play.name,bounty))
	wcsgroup.setUser(vic_play.userid,"wcs_bounty_kills",0)
	wcsgroup.setUser(vic_play.userid,"wcs_bounty_bounty",0)