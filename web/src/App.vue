<template>
    <div class="flex flex-col items-center justify-center">
        <header class="w-full max-w-[900px] mt-8 mb-8">
            <h1 class="text-4xl font-bold mb-8">HACKATHON IN ITALIA</h1>
            <p class="text-gray-700 text-justify text-sm">
                <strong>DISCLAIMER(S):</strong> Questo sito è un semplice 
                aggregatore automatico di hackathon trovabili online.
                Il progetto nasce dal desiderio di facilitare la scoperta di eventi e non è in alcun modo affiliato
                ad alcuna organizzazione.
                Gli eventi sono selezionati dai primi 50 risultati di
                ricerca con Custom Search JSON API per la query "Hackathon Italia"
                ed organizzati per mese grazie ad un LLM. 
                Vista la natura del sistema, ci potrebbero essere errori o omissioni.
            </p>
        </header>
        <div class="flex gap-8 max-w-[900px] justify-center w-full">
            <!--<div class="hidden md:block sticky top-0 self-start h-full pt-2 flex-1 max-w-[200px]">
                <NavList ref="navListRef" @scrollToMonth="scrollToMonth" />
            </div>-->
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

<style scoped>
/* Add your styles here */
</style>
