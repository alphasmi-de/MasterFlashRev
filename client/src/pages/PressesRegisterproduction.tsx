import api from '../config/axiosConfig';
import type React from 'react';
import { useEffect, useState, useCallback } from 'react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../App.css';
import '../index.css';
import '../output.css';
import { useLocation, useNavigate } from 'react-router-dom';
import OverWritePopUp from '../components/OverWritePopUp';
import Header from '../components/Header';

interface DataItem {
    id: number;
    press: string;
    molder_number: number;
    part_number: string;
    work_order: string;
    caliber: number | null;
    worked_hours: number;
    dead_time_cause_1: string;
    cavities: number;
    standard: number;
    proposed_standard: string;
    dead_time_cause_2: string;
    pieces_ok: number;
    efficiency: number;
    proposed_efficiency: number;
    date_time: string;
    shift: string;
    relay: boolean;
    editableField?: keyof DataItem;
}

const PressesRegisterProduction: React.FC = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const [editableData, setEditableData] = useState<DataItem[]>([]);
    const [selectedDate, setSelectedDate] = useState<string>(location.state?.date || '');
    const [selectedShift, setSelectedShift] = useState<string>(location.state?.shift || '');
    const [showModal, setShowModal] = useState<boolean>(false);
    const [overwrite, setOverwrite] = useState<boolean>(false);

    const groupDataItems = (data: DataItem[]): DataItem[] => {
        const groupedData: { [key: string]: DataItem } = {};

        data.forEach(item => {
            const partPrefix = item.part_number.split('-')[0];
            const key = `${item.press}-${item.molder_number}-${partPrefix}`;

            if (groupedData[key]) {
                groupedData[key].pieces_ok += item.pieces_ok;
            } else {
                groupedData[key] = { ...item, part_number: partPrefix };
            }
        });

        return Object.values(groupedData).sort((a, b) => a.press.localeCompare(b.press));
    };

    const fetchData = useCallback(async () => {
        if (!selectedDate || !selectedShift) {
            toast.error('Selecciona una fecha y un turno.');
            return;
        }
        try {
            const response = await api.post(
                '/get_production_press_by_date/',
                { date: selectedDate, shift: selectedShift },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                },
            );
            
            // Verificar si la respuesta tiene datos
            if (!response.data || response.data.error) {
                console.error('Error en la respuesta:', response.data?.error || 'No hay datos');
                toast.error('Error al cargar los datos de producción');
                return;
            }
            
            const responseData: DataItem[] = response.data;
            console.log('Datos recibidos:', responseData);

            const groupedData = groupDataItems(responseData);

            groupedData.forEach(item => {
                if (item.worked_hours > 0 && item.standard > 0) {
                    item.efficiency = (100 * item.pieces_ok) / (item.standard * item.worked_hours);
                } else {
                    item.efficiency = 0;
                }
                item.proposed_efficiency = 0;
            });

            console.log('Datos agrupados:', groupedData);

            setEditableData(groupedData);
        } catch (error) {
            console.error('Error fetching data:', error);
            toast.error('Error al cargar los datos de producción');
        }
    }, [selectedDate, selectedShift]);

    useEffect(() => {
        if (selectedDate) {
            fetchData();
        }
    }, [selectedDate, fetchData]);

    const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSelectedDate(e.target.value);
    };

    const handleShiftChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        setSelectedShift(e.target.value);
    };

    const handleDoubleClick = (index: number, field: keyof DataItem) => {
        const newData = [...editableData];
        newData[index] = {
            ...newData[index],
            editableField: field,
        };
        setEditableData(newData);
    };

    const handleBlur = (index: number) => {
        const newData = [...editableData];
        newData[index] = {
            ...newData[index],
            editableField: undefined,
        };
        setEditableData(newData);
    };

    const handleChange = (index: number, field: keyof DataItem, value: string | number) => {
        const newData = [...editableData];
        newData[index] = {
            ...newData[index],
            [field]: value,
        };

        // Calcular proposed_efficiency cuando se modifica proposed_standard
        if (field === 'proposed_standard') {
            const proposedStandard = parseFloat(value.toString());
            if (proposedStandard > 0 && newData[index].worked_hours > 0) {
                const proposedDecimal =
                    (100 * newData[index].pieces_ok) / (proposedStandard * newData[index].worked_hours);
                newData[index].proposed_efficiency = parseFloat(proposedDecimal.toFixed(2));
            } else {
                newData[index].proposed_efficiency = 0;
            }
        }

        // Calcular eficiencia (efficiency) cuando se modifica worked_hours
        if (field === 'worked_hours') {
            const workedHrs = Number(value);

            if (workedHrs > 0) {
                const decimal = 100 * (newData[index].pieces_ok / (newData[index].standard * workedHrs));
                const proposed_decimal =
                    100 * (newData[index].pieces_ok / (Number.parseFloat(newData[index].proposed_standard) * workedHrs));
                newData[index].efficiency = Number(decimal.toFixed(2));
                newData[index].proposed_efficiency = Number(proposed_decimal.toFixed(2));

            } else {
                newData[index].efficiency = 0;
                newData[index].proposed_efficiency = 0;
            }
        }

        setEditableData(newData);
    };

    const handleSave = async () => {
        const request = {
            date: selectedDate,
            shift: selectedShift,
            records: editableData.map(item => ({
                press: item.press,
                molder_number: item.molder_number,
                part_number: item.part_number,
                work_order: item.work_order,
                caliber: item.caliber || '',
                worked_hrs: item.worked_hours,
                dead_time_cause_1: item.dead_time_cause_1 || '',
                cavities: item.cavities,
                standard: item.standard,
                proposed_standard: item.proposed_standard || '',
                dead_time_cause_2: item.dead_time_cause_2 || '',
                pieces_ok: item.pieces_ok,
                efficiency: item.efficiency,
                proposed_efficiency: item.proposed_efficiency,
            })),
            overwrite: overwrite,
        };

        try {
            const response = await api.post('/save_production_records/', request, {
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (response.data.status === 'exists') {
                setShowModal(true);
            } else {
                toast.success('Datos guardados exitosamente.');
            }
        } catch (error) {
            console.error('Error al guardar los datos: ', error);
            toast.error('Hubo un error al guardar los datos.');
        }
    };

    const handleConfirmOverwrite = async () => {
        setOverwrite(true);
        setShowModal(false);

        try {
            const response = await api.post(
                '/save_production_records/',
                {
                    date: selectedDate,
                    shift: selectedShift,
                    records: editableData.map(item => ({
                        press: item.press,
                        molder_number: item.molder_number,
                        part_number: item.part_number,
                        work_order: item.work_order,
                        caliber: item.caliber || '',
                        worked_hrs: item.worked_hours,
                        dead_time_cause_1: item.dead_time_cause_1 || '',
                        cavities: item.cavities,
                        standard: item.standard,
                        proposed_standard: item.proposed_standard || '',
                        dead_time_cause_2: item.dead_time_cause_2 || '',
                        pieces_ok: item.pieces_ok,
                        efficiency: item.efficiency,
                        proposed_efficiency: item.proposed_efficiency,
                    })),
                    overwrite: true,
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                },
            );

            console.log(response);
            toast.success('Datos sobrescritos exitosamente.');
        } catch (error) {
            console.error('Error al sobrescribir los datos: ', error);
            toast.error('Hubo un error al sobrescribir los datos.');
        }
    };

    const handleEditClick = () => {
        const queryString = new URLSearchParams({
            date: selectedDate,
            shift: selectedShift,
        }).toString();

        navigate(`/edit_production_record?${queryString}`);
    };

    const calculateTotalProduction = (): number => {
        return editableData.reduce((total, item) => total + item.pieces_ok, 0);
    };

    return (
        <div className='min-h-screen flex flex-col px-7 py-4 md:px-10 md:py-6 bg-[#d7d7d7] h-full sm:h-screen'>
            <ToastContainer
                position='top-center'
                autoClose={false}
                newestOnTop
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                theme='colored'
            />
            <OverWritePopUp
                show={showModal}
                onClose={() => setShowModal(false)}
                onConfirm={handleConfirmOverwrite}
                message='Los datos ya existen. ¿Desea sobrescribirlos?'
            />
            <Header title='Registro Producción' goto='/press_production_records_summary' />

            <nav className='grid grid-cols-3 items-center gap-4'>
                <ul className=' col-start-2 flex justify-center gap-4'>
                    <li>
                        <label htmlFor='shifts' className='block mb-2 text-sm font-medium text-gray-900'>
                            Turno
                        </label>
                        <select
                            name='shifts select'
                            id='shifts'
                            value={selectedShift}
                            onChange={handleShiftChange}
                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                        >
                            <option value='' disabled>
                                Selecciona un turno
                            </option>
                            <option value='First'>First</option>
                            <option value='Second'>Second</option>
                            <option value='Free'>Free</option>
                        </select>
                    </li>
                    <li>
                        <label htmlFor='date' className='block mb-2 text-sm font-medium text-gray-900'>
                            Fecha
                        </label>
                        <input
                            id='date'
                            name='date'
                            type='date'
                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                            onChange={handleDateChange}
                            value={selectedDate}
                        />
                    </li>
                    <li className='flex justify-end p-2'>
                        <span className='text-lg font-medium'>Total Producción: {calculateTotalProduction()}</span>
                    </li>
                </ul>
                <div className='flex justify-end p-2 gap-4'>
                    <button
                        onClick={handleSave}
                        className='text-gray-900 bg-[#9ADD57] lg:text-sm hover:bg-[#9fe35b] focus:ring-4 focus:outline-none focus:ring-lime-300 font-medium rounded-lg text-sm px-5 py-2.5'
                    >
                        Guardar
                    </button>
                    <button
                        onClick={handleEditClick}
                        className='text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5'
                    >
                        Editar
                    </button>
                </div>
            </nav>

            <main className='relative overflow-x-auto shadow-md sm:rounded-lg mt-12'>
                <table className='w-full text-sm text-left text-gray-500'>
                    <thead className='text-xs text-gray-700 uppercase bg-gray-50'>
                        <tr>
                            <th scope='col' className='px-6 py-3 '>
                                # MP
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                No.Operador
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Orden de trabajo
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                No.Parte
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Cavidades
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Calibre
                            </th>
                            <th scope='col' className='px-6 py-3 bg-yellow-300'>
                                Causa de Tiempo muerto (Str.)
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Estándar por hora
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Estándar propuesto
                            </th>
                            <th scope='col' className='px-6 py-3 bg-yellow-300'>
                                Causa de tiempo muerto (Tiempo)
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Hrs Trabajadas
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Producción
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Eficiencia
                            </th>
                            <th scope='col' className='px-6 py-3'>
                                Eficiencia propuesta
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {editableData.map((item, index) => (
                            <tr
                                key={`${index}-${item.id}`}
                                className={`${item.relay ? 'bg-blue-100' : 'odd:bg-white even:bg-gray-50'} border-b`}
                            >
                                <th scope='row' className='px-6 py-4 font-medium text-gray-900 whitespace-nowrap'>
                                    {item.press}
                                </th>
                                <td className='px-6 py-4'>{item.molder_number}</td>
                                <td className='px-6 py-4'>{item.work_order}</td>
                                <td className='px-6 py-4'>{item.part_number}</td>
                                <td className='px-6 py-4' onClick={() => handleDoubleClick(index, 'cavities')}>
                                    {item.editableField === 'cavities' ? (
                                        <input
                                            type='text'
                                            value={item.cavities}
                                            onChange={e => handleChange(index, 'cavities', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.cavities}</span>
                                    )}
                                </td>
                                <td className='px-6 py-4' onClick={() => handleDoubleClick(index, 'caliber')}>
                                    {item.editableField === 'caliber' ? (
                                        <input
                                            type='text'
                                            value={item.caliber || ''}
                                            onChange={e => handleChange(index, 'caliber', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.caliber}</span>
                                    )}
                                </td>

                                <td
                                    className='px-6 py-4 bg-yellow-300'
                                    onClick={() => handleDoubleClick(index, 'dead_time_cause_1')}
                                >
                                    {item.editableField === 'dead_time_cause_1' ? (
                                        <input
                                            type='text'
                                            value={item.dead_time_cause_1 || ''}
                                            onChange={e => handleChange(index, 'dead_time_cause_1', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-yellow-300 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.dead_time_cause_1}</span>
                                    )}
                                </td>
                                <td className='px-6 py-4'>{item.standard}</td>
                                <td className='px-6 py-4' onClick={() => handleDoubleClick(index, 'proposed_standard')}>
                                    {item.editableField === 'proposed_standard' ? (
                                        <input
                                            type='text'
                                            value={item.proposed_standard}
                                            onChange={e => handleChange(index, 'proposed_standard', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.proposed_standard}</span>
                                    )}
                                </td>
                                <td
                                    className='px-6 py-4 bg-yellow-300'
                                    onClick={() => handleDoubleClick(index, 'dead_time_cause_2')}
                                >
                                    {item.editableField === 'dead_time_cause_2' ? (
                                        <input
                                            type='text'
                                            value={item.dead_time_cause_2 || ''}
                                            onChange={e => handleChange(index, 'dead_time_cause_2', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-yellow-300 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.dead_time_cause_2}</span>
                                    )}
                                </td>
                                <td className='px-6 py-4' onClick={() => handleDoubleClick(index, 'worked_hours')}>
                                    {item.editableField === 'worked_hours' ? (
                                        <input
                                            type='text'
                                            value={item.worked_hours || ''}
                                            onChange={e => handleChange(index, 'worked_hours', e.target.value)}
                                            onBlur={() => handleBlur(index)}
                                            className='bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
                                            autoFocus
                                        />
                                    ) : (
                                        <span>{item.worked_hours}</span>
                                    )}
                                </td>
                                <td className='px-6 py-4'>{item.pieces_ok}</td>
                                <td className='px-6 py-4'>{`${item.efficiency.toFixed(2)}%`}</td>
                                <td className='px-6 py-4'>{`${item.proposed_efficiency.toFixed(2)}%`}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </main>
        </div>
    );
};

export default PressesRegisterProduction;
