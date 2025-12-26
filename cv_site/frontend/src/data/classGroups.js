const CLASS_GROUPS = [
    {
        group: 'group_personnel',
        classes: [
            { key: 'class_civilian', label: 'Civilians', icon: '🧑' },
            { key: 'soldier', label: 'Soldier', icon: '🪖' },
        ]
    },
    {
        group: 'group_wheeled',
        classes: [
            { key: 'class_vehicle', label: 'Vehicle', icon: '🚙' },
            { key: 'apc', label: 'APC', icon: '🚐' },
        ]
    },
    {
        group: 'group_tracked',
        classes: [
            { key: 'lav', label: 'LAV', icon: '🛺' },
            { key: 'tank', label: 'Tank', icon: '🛡️' },
            { key: 'ifv', label: 'IFV', icon: '🚛' },
        ]
    },
    {
        group: 'group_artillery',
        classes: [
            { key: 'class_mrls', label: 'MLRS', icon: '🚀' },
        ]
    },
    {
        group: 'group_aa',
        classes: [
            { key: 'class_aa', label: 'Air Defense', icon: '🛡️' },
            { key: 'radar', label: 'Radar', icon: '📡' },
        ]
    },
    {
        group: 'group_air',
        classes: [
            { key: 'class_heli', label: 'Helicopter', icon: '🚁' },
            { key: 'class_plane', label: 'Plane', icon: '✈️' },
        ]
    },
];

export default CLASS_GROUPS; 