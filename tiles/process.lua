-- BinRadar "bins" layer.
--
-- Matches OSM nodes tagged amenity=waste_basket, amenity=waste_disposal,
-- amenity=recycling, or bin=yes. The class attribute carries the matched
-- type through, so a consumer can tell the classes apart instead of
-- lumping them into one indistinguishable point type.
--
-- bin=yes is treated as class=waste_basket, but flagged precision=low.
-- It is commonly added to a bench or similar object rather than a
-- dedicated waste basket node, so it is a weaker signal than a proper
-- amenity tag.
--
-- Each class carries one optional class-specific tag, recorded only when
-- present and never required for a match: waste=* for the two waste
-- classes and for bin=yes, recycling_type=* for recycling.
--
-- All matched objects are almost always mapped as nodes in OSM, so
-- way_function has nothing to do.
--
-- The OSM node id is recorded as an explicit id attribute (see
-- set_common_attributes) and, separately, as the MVT feature id through
-- settings.include_ids in config.json. Either lets a consumer match a
-- feature back to its source node.
--
-- node_keys/way_keys: kept as a pure perf/defensive win, not a
-- correctness requirement — the pipeline now runs tilemaker via
-- ghcr.io/systemed/tilemaker (see claim-and-build/action.yml), not
-- apt's tilemaker 2.4.0. That old apt build was the actual cause of a
-- past incident: its GetSignificantNodeKeys read `node_keys` via kaguya
-- with no nil-guard, so an undefined `node_keys` made every region's
-- build abort with "kaguya::LuaTypeMismatch" converting Lua nil to a
-- C++ vector<string>, before a single node was processed. Current
-- tilemaker guards that read, so it's no longer required — but the
-- image tag isn't pinned to a release (it floats with upstream's
-- master), so keeping node_keys/way_keys defined costs nothing and
-- avoids depending on that guard staying in place. Must list every key
-- node_function branches on (amenity, bin) or a matching node gets
-- silently skipped instead of processed.
node_keys = { "amenity", "bin" }
way_keys = {}

local function set_common_attributes()
	Attribute("id", Id())

	local name = Find("name")
	if name ~= "" then
		Attribute("name", name)
	end

	local opening_hours = Find("opening_hours")
	if opening_hours ~= "" then
		Attribute("opening_hours", opening_hours)
	end
end

-- Records `key` as an attribute only when the node actually carries it,
-- so an absent optional tag adds nothing to the tile rather than an
-- empty string.
local function record_optional_attribute(key)
	local value = Find(key)
	if value ~= "" then
		Attribute(key, value)
	end
end

-- Starts a `bins` feature for one matched node. Everything the classes
-- share lives here; the caller adds only what is specific to its class.
local function begin_bin(class)
	Layer("bins", false)
	Attribute("class", class)
end

function node_function(node)
	local amenity = Find("amenity")

	-- The class name and the amenity value are the same string for these
	-- two, so the matched value carries straight through.
	if amenity == "waste_basket" or amenity == "waste_disposal" then
		begin_bin(amenity)
		record_optional_attribute("waste")
	elseif amenity == "recycling" then
		begin_bin("recycling")
		record_optional_attribute("recycling_type")
	elseif Find("bin") == "yes" then
		begin_bin("waste_basket")
		Attribute("precision", "low")
		record_optional_attribute("waste")
	else
		return
	end

	set_common_attributes()
end

function way_function(way)
end
