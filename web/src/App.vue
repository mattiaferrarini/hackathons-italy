<template>
    <div class="flex flex-col items-center justify-center">
        <header class="w-full max-w-[1200px] mt-8 mb-8">
            <h1 class="text-4xl font-bold mb-8">HACKATHONS IN ITALIA {{ currentYear }}</h1>
            <p class="text-gray-700">
                <strong>DISCLAIMER(S):</strong> Questo sito è un semplice <span class="text-emerald-600">aggregatore
                    automatico</span> di hackathon elencati online.
                Il progetto nasce dal desiderio di facilitare la scoperta di eventi e non è in alcun modo affiliato
                a nessuna organizzazione.
                Gli elementi elencati sono selezionati dai <span class="text-emerald-600">primi 100 risultati di
                    ricerca su DuckDuckGo</span> per la query <i>hackathon italia {anno_corrente}</i>
                ed organizzati per mese in base all'esplicita menzione di uno o più mesi nei siti degli eventi.
                Quindi: (1) alcuni elementi potrebbero non essere hackathon, (2) alcuni eventi potrebbero non essere
                elencati,
                (3) alcuni eventi potrebbero essere elencati in mesi sbagliati o in molteplici mesi.
            </p>
        </header>
        <div class="flex gap-8 max-w-[1200px] justify-center w-full">
            <div class="hidden md:block sticky top-0 self-start h-full pt-2 flex-1 max-w-[200px]">
                <NavList ref="navListRef" @scrollToMonth="scrollToMonth" />
            </div>
            <main class="w-full">
                <MonthList ref="monthListRef" @visibleMonthChanged="updateNavList" />
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import MonthList from './components/MonthList.vue';
import NavList from './components/NavList.vue';

const currentYear = ref(new Date().getFullYear());
const monthListRef = ref(null);
const navListRef = ref(null);

const scrollToMonth = (month) => {
    if (monthListRef.value) {
        monthListRef.value.scrollToMonth(month);
    }
}

const updateNavList = (month) => {
    if (navListRef.value) {
        navListRef.value.updateActiveMonth(month);
    }
}

</script>

<style scoped></style>
