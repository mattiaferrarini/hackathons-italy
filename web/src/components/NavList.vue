<template>
    <nav class="border-gray-300 border-2 w-[180px] py-4 px-4 rounded-lg flex flex-col gap-2 text-gray-600">
        <h2 class="text-center font-bold mb-2">VAI A</h2>
        <button v-for="month in months" :key="month" class="hover:font-bold text-sm" :class="{'font-bold text-emerald-600': month===activeMonth}" @click="triggerScroll(month)">
            {{ month.toUpperCase() }}
        </button>
    </nav>
</template>

<script>
export default {
    name: 'NavList',
    emits: ['scrollToMonth'],
    data() {
        return {
            months: [],
            activeMonth: null
        };
    },
    mounted() {
        fetch(`${import.meta.env.BASE_URL}hackathons.json`)
            .then(response => response.json())
            .then(data => {
                this.months = this.extractHackathonMonths(data);
            })
            .catch(error => {
                console.error('Error fetching hackathons data:', error);
            });
        window.addEventListener('scroll', this.checkVisibleMonths);
        this.$nextTick(this.checkVisibleMonths);
    },
    methods: {
        triggerScroll(month) {
            this.$emit('scrollToMonth', month);
        },
        updateActiveMonth(month) {
            this.activeMonth = month;
        },
        extractHackathonMonths(hackathons) {
            const months = [
                'gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'
            ];
            const grouped = {};
            hackathons.forEach(hackathon => {
                if (!hackathon.starting_date) return;
                const date = new Date(hackathon.starting_date);
                const monthIndex = date.getMonth();
                const year = date.getFullYear();
                const key = `${months[monthIndex]} ${year}`;
                if (!grouped[key]) {
                    grouped[key] = [];
                }
                grouped[key].push(hackathon);
            });
            // Sort the groups by year and month
            const sortedKeys = Object.keys(grouped).sort((a, b) => {
                const [monthA, yearA] = a.split(' ');
                const [monthB, yearB] = b.split(' ');
                const dateA = new Date(`${yearA}-${months.indexOf(monthA) + 1}-01`);
                const dateB = new Date(`${yearB}-${months.indexOf(monthB) + 1}-01`);
                return dateA - dateB;
            });
            return sortedKeys;
        },
    }
};
</script>