<template>
    <nav class="border-gray-300 border-2 w-[180px] py-4 px-8 rounded-lg flex flex-col gap-2 text-gray-600">
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
            months: ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno', 'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'],
            activeMonth: null
        };
    },
    methods: {
        triggerScroll(month) {
            this.$emit('scrollToMonth', month);
        },
        updateActiveMonth(month) {
            this.activeMonth = month;
        }
    }
};
</script>