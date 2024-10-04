<template>
    <div class="month-list w-full">
        <ul class="flex flex-col gap-8 w-full">
            <li v-for="(hackathons, month) in hackathonsData" :key="month" :ref="month" :data-month="month">
                <h2 class="text-lg font-semibold mb-2 border-gray-800">{{ month.toUpperCase() }}</h2>
                <ul class="pl-1 sm:pl-2">
                    <li v-for="hackathon in hackathons" :key="hackathon.href" class="mb-3 sm:mb-0 hover:bg-emerald-50">
                        <a :href="hackathon.href" target="_blank" class="block no-underline">
                            <div
                                class="py-2 pl-3 sm:pl-4 border-l-2 border-gray-400 hover:border-l-4 hover:border-emerald-600 pr-1 sm:pr-2 flex flex-col gap-2 sm:flex-row sm:justify-between">
                                <span class="text-gray-700">{{ hackathon.title }} </span>
                                <span class="text-emerald-600">{{ getDomain(hackathon.href) }}</span>
                            </div>
                        </a>
                    </li>
                </ul>
            </li>
        </ul>
    </div>
</template>

<script>
export default {
    name: 'MonthList',
    emits: ['visibleMonthChanged'],
    data() {
        return {
            hackathonsData: {},
            visibleMonth: null
        };
    },
    mounted() {
        fetch(`${import.meta.env.BASE_URL}hackathons.json`)
            .then(response => response.json())
            .then(data => {
                this.hackathonsData = data;
            })
            .catch(error => {
                console.error('Error fetching hackathons data:', error);
            });
        window.addEventListener('scroll', this.checkVisibleMonths);
        this.$nextTick(this.checkVisibleMonths);
    },
    methods: {
        checkVisibleMonths() {
            const visibleMonths = [];
            Object.keys(this.$refs).forEach(month => {
                if (this.$refs[month] && this.$refs[month][0]) {
                    const rect = this.$refs[month][0].getBoundingClientRect();
                    if (rect.top >= 0 && rect.bottom <= window.innerHeight) {
                        visibleMonths.push(this.$refs[month][0].dataset.month);
                    }
                }
            });
            if (visibleMonths.length > 0) {
                visibleMonths.sort((a, b) => {
                    const rectA = this.$refs[a][0].getBoundingClientRect();
                    const rectB = this.$refs[b][0].getBoundingClientRect();
                    return rectA.top - rectB.top;
                });
                this.visibleMonth = visibleMonths[0];
            }
        },
        scrollToMonth(month) {
            const currentMonthElement = this.$refs[month];
            if (currentMonthElement && currentMonthElement[0]) {
                currentMonthElement[0].scrollIntoView({ behavior: 'smooth' });
            }
        },
        getDomain(url) {
            try {
                const { hostname } = new URL(url);
                return hostname;
            } catch (e) {
                console.error('Invalid URL:', url);
                return url;
            }
        }
    },
    watch: {
        visibleMonth(newMonth) {
            this.$emit('visibleMonthChanged', newMonth);
        }
    }
};
</script>

<style scoped></style>